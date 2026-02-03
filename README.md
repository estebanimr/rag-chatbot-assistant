# RAG Chatbot Assistant
This repository contains a Retrieval-Augmented Generation (RAG) chatbot assistant built
as a technical challenge. It ingests content from web and PDF sources, builds a
vector index, and exposes a simple API for question answering.

## Architecture (high level)
- FastAPI + LangServe serve the RAG chain API.
- Ollama provides chat + embedding models.
- Chroma stores the vector index on disk.
- Ingestion loads web pages and PDFs to build the index.

## Requirements
- Docker and Docker Compose (plugin)

## Configuration
Copy the example env file and fill required values:
```
cp .env.example .env
```
Required:
- `OLLAMA_CHAT_MODEL`
- `OLLAMA_EMBED_MODEL`

Other envs used by the app (check `.env.example`):

## Run locally (Docker Compose)
Build and start:
```
docker compose up --build
```

Compose flow:
1) Pulls Ollama models
2) Runs ingestion (creates `index_store/current.txt`)
3) Starts the API

## Test the API
Default URL: `http://localhost:8000`

Founded question:
```
curl -s http://localhost:8000/rag/invoke \
  -H "Content-Type: application/json" \
  -d "{\"input\":\"When was the company founded?\"}"
```

Services question:
```
curl -s http://localhost:8000/rag/invoke \
  -H "Content-Type: application/json" \
  -d "{\"input\":\"What services does Promtior offer?\"}"
```

LangServe provides a playground endpoint when enabled (usually `/rag/playground`).

## AWS Instance:
- Call the API using the public IP, e.g.:
```
curl http://3.138.34.121:8000/health
```

## Project documentation
- `doc/project-overview.md`
- `doc/component-diagram.png`