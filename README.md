# Verified Insight Engine

An agentic RAG system with self-correcting attribution loops for family and consumer market intelligence.

---

## Overview

The Verified Insight Engine is a locally-run AI pipeline that generates **source-attributed, hallucination-resistant insights** from market research documents. Built for the family and consumer intelligence sector, it prioritises factual accuracy over creative generation by implementing a self-correction loop that actively searches for contradictory evidence before producing any output.

All processing runs locally via Ollama - no data leaves your machine.

---

## Architecture

```
User Query
    ↓
ChromaDB Vector Store (semantic document search)
    ↓
LLM generates initial insight + claims
    ↓
Self-Correction Node (re-queries store for contradictory evidence)
    ↓
Attribution Agent (maps every claim to a source document ID)
    ↓
Verified Insight + Sources + Confidence Score
```

---

## Tech Stack

| Component | Tool |
|---|---|
| Agentic pipeline | LangGraph |
| LLM | Ollama (llama3.2 - local) |
| Vector store | ChromaDB |
| Embeddings | Ollama nomic-embed-text |
| Frontend | Streamlit |
| Language | Python 3.10+ |

---

## Key Features

- **Self-correcting loop** - after generating an insight, the agent re-queries ChromaDB specifically to find contradictory evidence
- **Source attribution** - every claim is mapped to a specific document ID before output is released
- **Confidence scoring** - insights below threshold are flagged for human review
- **Privacy-preserving** - fully local, no external API calls, no PII exposure
- **Family sector focused** - ingests UNICEF reports, Alan Turing Institute publications, and consumer research datasets

---

## Project Structure

```
verified-insight-engine/
│
├── data/                  # Raw PDF/text source documents
├── ingest.py              # Document loader and ChromaDB embedder
├── graph.py               # LangGraph agentic pipeline
├── app.py                 # Streamlit frontend
├── requirements.txt       # Dependencies
└── .env                   # Environment config
```

---

## Setup

```bash
# 1. Pull the model
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API Key (Optional for Shared Access)
# Create a .env file from the example
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
# If this is set, users will not need to enter their own key in the UI.

# 4. Ingest documents
python ingest.py

# 5. Run the app
streamlit run app.py
```

-
## Author
**Richard Ogundele**  - 
