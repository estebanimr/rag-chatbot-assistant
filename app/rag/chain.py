from __future__ import annotations

from pathlib import Path
from typing import Iterable

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.config.settings import Settings

_SERVICE_SOURCE_URL = "https://www.promtior.ai/service"


def _load_active_run_dir(settings: Settings) -> Path:
    index_dir = Path(settings.index_dir)
    pointer_path = index_dir / "current.txt"
    raw_value = pointer_path.read_text(encoding="utf-8").strip()
    if not raw_value:
        raise ValueError(f"Index pointer is empty: {pointer_path}")
    if ":" in raw_value:
        raise ValueError(
            "Index pointer contains a Windows absolute path. "
            "Re-run ingestion in the current environment to regenerate it."
        )
    run_dir = Path(raw_value)
    if run_dir.is_absolute():
        raise ValueError(
            "Index pointer must be a relative path. "
            "Re-run ingestion in the current environment to regenerate it."
        )
    run_dir = index_dir / run_dir
    return run_dir


def _format_documents(docs: Iterable[Document]) -> str:
    chunks: list[str] = []
    for doc in docs:
        chunks.append(doc.page_content or "")
    return "\n\n---\n\n".join(chunks)


def _format_service_titles(docs: Iterable[Document]) -> str:
    titles: list[str] = []
    for doc in docs:
        first_line = (doc.page_content or "").split("\n", 1)[0].strip()
        if first_line:
            titles.append(first_line)
    return "\n".join(titles)


def _is_services_question(question: str) -> bool:
    """Check if a question is about services for retrieval routing."""
    lowered = question.lower()
    return "service" in lowered or "services" in lowered


def build_rag_chain(settings: Settings) -> Runnable:
    run_dir = _load_active_run_dir(settings)
    embeddings = OllamaEmbeddings(
        base_url=settings.ollama_base_url,
        model=settings.ollama_embed_model,
    )
    vectorstore = Chroma(
        persist_directory=str(run_dir),
        embedding_function=embeddings,
    )
    default_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": settings.retriever_top_k, "fetch_k": 20, "lambda_mult": 0.5}
    )
    services_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": settings.retriever_top_k,
            "fetch_k": 20,
            "lambda_mult": 0.5,
            "filter": {"source": _SERVICE_SOURCE_URL},
        },
    )

    def _retrieve_documents(question: str) -> list[Document]:
        # Avoid retrieval mixing for services questions by scoping to the service page.
        if _is_services_question(question):
            docs = services_retriever.invoke(question)
            if docs:
                return docs
        return default_retriever.invoke(question)

    def _build_context(question: str) -> str:
        docs = _retrieve_documents(question)
        if _is_services_question(question):
            return _format_service_titles(docs)
        return _format_documents(docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a factual assistant. Use ONLY the provided context. "
                "Do not mention context, sources, pages, documents, or PDFs. "
                "Do not greet. Do not restate the question. "
                "If the answer is a single fact, reply in 1 sentence. Otherwise, use up to 3 sentences. "
                "If the answer is not explicitly in the context, respond exactly: "
                '"I don\'t know based on the provided context."',
            ),
            ("human", "Question: {question}\n\nContext:\n{context}"),
        ]
    )
    model = ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_chat_model,
    )

    return (
        {
            "context": RunnableLambda(_build_context),
            "question": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )
