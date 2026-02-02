from fastapi import FastAPI
from langserve import add_routes

from app.config.settings import settings
from app.rag.chain import build_rag_chain

app = FastAPI(title="Chatbot Assistant API")

rag_chain = build_rag_chain(settings)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


add_routes(app, rag_chain, path="/rag")

