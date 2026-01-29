from fastapi import FastAPI
from langchain_core.runnables import RunnableLambda
from langserve import add_routes

app = FastAPI(title="RAG API (Skeleton)")

test_chain = RunnableLambda(lambda x: x)

add_routes(app, test_chain, path="/test")

