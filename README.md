# rag-chatbot-assistant
This repository was created as a technical assessment.

## Run locally
- Create and activate a virtual environment: `python -m venv .venv` and then `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux).
- Install requirements: `python -m pip install -r requirements.txt`
- Install and run Ollama (https://ollama.com) and pull your chat/embedding models.
- Set env vars: `OLLAMA_BASE_URL`, `OLLAMA_CHAT_MODEL`, `OLLAMA_EMBED_MODEL`
- Run ingestion: `python -m app.ingest.ingest`
- Run API: `uvicorn app.api.main:app --reload`
- Test services: `curl -s http://localhost:8000/rag/invoke -H "Content-Type: application/json" -d "{\"input\":\"What services does Promtior offer?\"}"`
- Test founded: `curl -s http://localhost:8000/rag/invoke -H "Content-Type: application/json" -d "{\"input\":\"When was Promtior founded?\"}"`

## Local run with Docker
- Copy env file: `cp .env.example .env` and set `OLLAMA_CHAT_MODEL` / `OLLAMA_EMBED_MODEL`
- Build and start: `docker compose up --build`
- Test services: `curl -s http://localhost:8000/rag/invoke -H "Content-Type: application/json" -d "{\"input\":\"What services does Promtior offer?\"}"`

Re-ingest: `FORCE_REINGEST=1 docker compose up --build ingest`