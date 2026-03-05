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

# 3. Ingest documents
python ingest.py

# 4. Run the app
streamlit run app.py
```

---

## Use Case Example

> **Query:** "How has screen time among children aged 5-10 changed since 2022?"
>
> **Engine process:**
> 1. Retrieves relevant passages from ingested reports
> 2. Generates insight with specific claims
> 3. Self-correction node searches for contradictory data
> 4. Attribution agent links each claim to source document
> 5. Outputs verified insight with confidence score and citations

---

## Interview Talking Points

- "I built a self-critiquing RAG system that prioritises factual accuracy over generation speed"
- "The self-correction node actively tries to disprove its own output before releasing it"
- "Running on Ollama means sensitive family data never leaves the local environment - GDPR by design"
- "The attribution layer means every insight is auditable back to a primary source"

---

## Author

**Richard Ogundele**  
AI Strategist | MSc Artificial Intelligence (Distinction), Manchester Metropolitan University  
[linkedin.com/in/richardogundele](https://linkedin.com/in/richardogundele)
