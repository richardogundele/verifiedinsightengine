"""
ingest.py
Loads PDF/text documents from the data/ folder,
splits them into chunks, and stores embeddings in ChromaDB.
"""

import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# --- Config ---
DATA_DIR = "./data"
CHROMA_DIR = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def load_documents(data_dir: str):
    """Load all PDFs and text files from the data directory."""
    docs = []
    path = Path(data_dir)

    if not path.exists():
        print(f"[ERROR] Data directory '{data_dir}' not found. Create it and add your documents.")
        return docs

    for file in path.iterdir():
        if file.suffix == ".pdf":
            print(f"[LOADING] {file.name}")
            loader = PyPDFLoader(str(file))
            docs.extend(loader.load())
        elif file.suffix == ".txt":
            print(f"[LOADING] {file.name}")
            loader = TextLoader(str(file), encoding="utf-8")
            docs.extend(loader.load())

    print(f"\n[INFO] Loaded {len(docs)} pages/documents total.")
    return docs


def split_documents(docs):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"[INFO] Split into {len(chunks)} chunks.")
    return chunks


def embed_and_store(chunks):
    """Embed chunks and store in ChromaDB."""
    print(f"\n[INFO] Embedding with Ollama model: {EMBED_MODEL}")
    print("[INFO] This may take a few minutes on first run...\n")

    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name="insights"
    )

    print(f"[SUCCESS] {len(chunks)} chunks stored in ChromaDB at '{CHROMA_DIR}'")
    return vectorstore


def main():
    print("=" * 50)
    print("  Verified Insight Engine - Document Ingestion")
    print("=" * 50)

    docs = load_documents(DATA_DIR)

    if not docs:
        print("\n[INFO] No documents found. Add PDFs or .txt files to the ./data folder and re-run.")
        return

    chunks = split_documents(docs)
    embed_and_store(chunks)

    print("\n[DONE] Ingestion complete. Run: streamlit run app.py")


if __name__ == "__main__":
    main()
