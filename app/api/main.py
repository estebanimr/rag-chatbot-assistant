from fastapi import FastAPI
from langchain_core.runnables import RunnableLambda
from langserve import add_routes

from app.config.settings import settings
from app.rag.chain import build_rag_chain

app = FastAPI(title="RAG API (Skeleton)")

test_chain = RunnableLambda(lambda x: x)
rag_chain = build_rag_chain(settings)

add_routes(app, test_chain, path="/test")
add_routes(app, rag_chain, path="/rag")

