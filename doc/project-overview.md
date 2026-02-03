## Project Overview

I approached the challenge by implementing a minimal but complete RAG pipeline end-to-end: ingestion + indexing + an API that can answer questions using retrieved context only. Since the evaluation depends a lot on reproducibility, I focused on a stable “one command up” setup using Docker, and on keeping the architecture simple to follow.

The solution has two main stages:

**1) Ingestion & indexing (offline step, automated in Compose):**  
I load the knowledge base from two types of sources: a PDF (extra information about Promtior) and a web page (Promtior services). After loading, I normalize the text (mainly whitespace cleanup) to avoid noisy artifacts that degrade retrieval. Then the content is chunked and embedded using Ollama embeddings, and stored in a persistent Chroma vector database. The index is written to a shared Docker volume so it survives restarts.

**2) Question answering (online step via API):**  
When a request arrives to the RAG endpoint, the API retrieves the most relevant chunks from Chroma (using MMR to reduce redundancy), injects them into a constrained prompt (“answer only using the provided context”), and calls the Ollama chat model to generate a short factual response.

**3) Deployment (AWS runtime environment):**  
To make the solution accessible, I deployed the same containerized setup to an AWS EC2 instance. The goal was to keep parity with local development: the same Docker image and Docker Compose orchestration run in EC2, and the API becomes reachable through the instance public IP (and the configured inbound rules / ports).

### Main challenges encountered and how I overcame them

**1) Data quality for retrieval (biggest challenge):**  
The hardest part wasn’t wiring the components together — it was getting the retriever to consistently bring the “right” pieces of context, especially for the services question. Early on, the index contained a lot of “distractor” content (navigation/cookie banners on the website, and non-business pages in the PDF such as technical test instructions). This caused retrieval to return relevant-looking but not useful chunks, which pushed the model to answer with generic marketing text or mixed information.

I iterated on the ingestion pipeline to improve the quality of the documents being indexed: normalizing whitespace, reducing obvious noise, and trying to structure the web content in a more meaningful way. After several attempts, I decided to keep the solution pragmatic rather than perfect: the goal became “retrieve something clearly related and answer based on it” instead of over-engineering a brittle scraper with lots of hardcoded page rules that could break if the site changes. In practice, this meant keeping a simpler loader and focusing on making the retrieval stable enough to answer the two core questions reliably.

**2) Model availability in Ollama (embeddings/chat):**  
When running everything in containers, ingestion failed because the embedding model wasn’t available yet (Ollama returns “model not found” until it’s pulled). I solved this by adding a dedicated `ollama-models-pull` step in Docker Compose that pulls both the embedding model and the chat model through Ollama’s HTTP API before ingestion starts.

**3) Working in a new area (RAG):**  
This challenge also forced me to work hands-on with concepts that were relatively new to me: how embeddings represent text, why chunk size/overlap matter, how retrieval quality impacts generation, and how to separate and format documents so the model receives context that’s actually usable. The final implementation reflects that learning curve: I focused on understanding each stage (load → normalize → chunk → embed → retrieve → generate) and making the system observable through small sanity checks and retrieval inspection during development.

Overall, I intentionally prioritized simplicity, redeable code, and clear responsibility boundaries per file/module. Instead of building a large complex pipeline.