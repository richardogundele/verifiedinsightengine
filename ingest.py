""" Scrapes live data from DataScrap sources, splits into chunks, and stores embeddings in ChromaDB. """

import sys
import json
import os
from datetime import datetime
sys.path.insert(0, ".")

from data.datascrap import DataScrap
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# --- Config ---
CHROMA_DIR = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def load_from_scrapers() -> list:
    """
    Pull live data from all three DataScrap sources and convert
    each record into a LangChain Document so it flows through
    the same split → embed → store pipeline as local files.
    """
    from langchain_core.documents import Document

    ds = DataScrap()
    all_records = []

    # Run all three scrapers
    all_records.extend(ds.scrape_unicef())
    all_records.extend(ds.scrape_ofcom())
    all_records.extend(ds.scrape_turing())

    docs = []
    for record in all_records:
        # Page content = the URL (what we'll embed / retrieve)
        content = record.get("url", "")
        # Metadata carries everything else for citation / filtering
        metadata = {k: v for k, v in record.items() if k != "url"}
        docs.append(Document(page_content=content, metadata=metadata))

    # Save raw records to JSON/TXT exports before conversion
    save_scraped_data(all_records)

    print(f"[SCRAPERS] {len(docs)} document(s) collected from live sources.")
    return docs


def save_scraped_data(records: list, export_dir: str = "./data/exports") -> str:
    """
    Persist scraped records to disk before embedding.
    Writes two files into *export_dir*:
      - scraped_<timestamp>.json  – full structured data (machine-readable)
      - scraped_<timestamp>.txt   – human-readable report
    Returns the base filename used (without extension).
    """
    os.makedirs(export_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"scraped_{timestamp}"

    # --- JSON export ---
    json_path = os.path.join(export_dir, f"{base_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # --- Human-readable text export ---
    txt_path = os.path.join(export_dir, f"{base_name}.txt")
    sources = {}
    for r in records:
        sources.setdefault(r.get("source", "unknown"), []).append(r)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"  Verdict Insight Engine – Scraped Data Export\n")
        f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"  Total records: {len(records)}\n")
        f.write("=" * 70 + "\n\n")

        for source, items in sources.items():
            f.write(f"{'─' * 60}\n")
            f.write(f"  SOURCE: {source.upper()}  ({len(items)} record(s))\n")
            f.write(f"{'─' * 60}\n")
            for i, item in enumerate(items, 1):
                f.write(f"  [{i}] {item.get('title', '(no title)')}\n")
                f.write(f"       URL : {item.get('url', 'N/A')}\n")
                # Print any extra metadata fields
                extras = {k: v for k, v in item.items() if k not in ('source', 'title', 'url')}
                for k, v in extras.items():
                    f.write(f"       {k.capitalize():5}: {v}\n")
                f.write("\n")

    print(f"[EXPORT] JSON  -> {json_path}")
    print(f"[EXPORT] Text  -> {txt_path}")
    return base_name


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
    print("  Verdict Insight Engine - Document Ingestion")
    print("=" * 50)

    # Pull everything from live scrapers (UNICEF, Ofcom, Turing)
    docs = load_from_scrapers()

    if not docs:
        print("\n[INFO] No data scraped. Check your internet connection or scraper output.")
        return

    chunks = split_documents(docs)
    embed_and_store(chunks)

    print("\n[DONE] Ingestion complete. Run: streamlit run app.py")
    
if __name__ == "__main__":
    main()
