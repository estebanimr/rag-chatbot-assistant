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


def _load_active_run_dir(settings: Settings) -> Path:
    index_dir = Path(settings.index_dir)
    pointer_path = index_dir / "current.txt"
    raw_value = pointer_path.read_text(encoding="utf-8").strip()
    if not raw_value:
        raise ValueError(f"Index pointer is empty: {pointer_path}")
    run_dir = Path(raw_value)
    if not run_dir.is_absolute():
        run_dir = index_dir / run_dir
    return run_dir


def _format_documents(docs: Iterable[Document]) -> str:
    chunks: list[str] = []
    for doc in docs:
        chunks.append(doc.page_content or "")
    return "\n\n---\n\n".join(chunks)


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
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": settings.retriever_top_k, "fetch_k": 20, "lambda_mult": 0.5}
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a factual assistant. Use ONLY the provided context. "
                "Answer with the minimal direct answer; do not add prefaces like "
                "'According to the context' or 'Based on the context'. "
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
            "context": retriever | RunnableLambda(_format_documents),
            "question": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )
