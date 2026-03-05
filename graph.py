""" 
LangGraph agentic pipeline with:
- Retrieval node
- Insight generation node
- Self-correction node (searches for contradictory evidence)
- Attribution node (maps claims to source documents)
"""

from typing import TypedDict, List, Optional
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langgraph.graph import StateGraph, END

# --- Config ---
CHROMA_DIR = "./chroma_db"
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
TOP_K = 5
CONFIDENCE_THRESHOLD = 0.6

# --- State Schema ---
class InsightState(TypedDict):
    query: str
    retrieved_docs: List[Document]
    web_context: str
    initial_insight: str
    contradictions: List[Document]
    final_insight: str
    sources: List[dict]
    confidence_score: float
    flagged_for_review: bool


# --- Shared resources ---
def get_vectorstore():
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="insights"
    )

def get_llm():
    return ChatOpenAI(model=LLM_MODEL, temperature=0.2)


# --- Node 1: Retrieve relevant documents ---
def retrieve_node(state: InsightState) -> InsightState:
    print("[NODE] Retrieving relevant documents...")
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(state["query"], k=TOP_K)
    return {**state, "retrieved_docs": docs}


# --- Node 2: Live Web Search Enrichment ---
def web_search_node(state: InsightState) -> InsightState:
    print("[NODE] Querying live internet for enrichment...")
    try:
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=3)
        search = DuckDuckGoSearchResults(api_wrapper=wrapper)
        # Search the live web for the exact user query
        web_results = search.invoke(state["query"])
    except Exception as e:
        print(f"[WARNING] Web search failed: {e}")
        web_results = "No live web results retrieved."
        
    return {**state, "web_context": web_results}


# --- Node 3: Generate initial insight ---
def generate_insight_node(state: InsightState) -> InsightState:
    print("[NODE] Generating initial insight...")
    llm = get_llm()

    context = "\n\n".join([
        f"[INTERNAL SOURCE {i+1}]: {doc.metadata.get('title', 'Unknown Title')} ({doc.page_content})"
        for i, doc in enumerate(state["retrieved_docs"])
    ])

    prompt = f"""You are a market intelligence analyst specialising in the family and consumer sector.

Using ONLY the documents and LIVE WEB DATA provided below, answer the following query with specific, factual claims.
For each claim you make, you MUST reference where it comes from using [INTERNAL SOURCE X] or [WEB SOURCE].
Do not invent or assume any information not present in the evidence.

Query: {state["query"]}

INTERNAL CORPORATE DOCUMENTS:
{context}

LIVE WEB ENRICHMENT DATA:
[WEB SOURCE]: {state["web_context"]}

Provide a clear, structured insight with inline document references:"""

    response = llm.invoke(prompt)
    return {**state, "initial_insight": response.content}


# --- Node 3: Self-correction - search for contradictions ---
def self_correct_node(state: InsightState) -> InsightState:
    print("[NODE] Running self-correction check...")
    vectorstore = get_vectorstore()

    # Build a contradiction query from the initial insight
    llm = get_llm()
    contradiction_prompt = f"""Given this insight: "{state["initial_insight"][:300]}"

Write a short search query (max 15 words) that would find CONTRADICTORY or opposing evidence to this insight."""

    contradiction_query = llm.invoke(contradiction_prompt).content.strip()
    print(f"[NODE] Contradiction search query: {contradiction_query}")

    contradiction_docs = vectorstore.similarity_search(contradiction_query, k=3)
    return {**state, "contradictions": contradiction_docs}


# --- Node 4: Attribution and final output ---
def attribution_node(state: InsightState) -> InsightState:
    print("[NODE] Building attributed final insight...")
    llm = get_llm()

    supporting_context = "\n\n".join([
        f"SUPPORTING [INTERNAL SOURCE {i+1}]: {doc.metadata.get('title', 'Unknown Title')} ({doc.page_content})"
        for i, doc in enumerate(state["retrieved_docs"])
    ])

    offset = len(state["retrieved_docs"])
    contradiction_context = "\n\n".join([
        f"CONTRADICTING [INTERNAL SOURCE {offset + i + 1}]: {doc.metadata.get('title', 'Unknown Title')} ({doc.page_content})"
        for i, doc in enumerate(state["contradictions"])
    ]) if state["contradictions"] else "No significant contradictions found."

    prompt = f"""You are a rigorous market intelligence analyst. Your job is to produce a VERIFIED insight.

Original Query: {state["query"]}

Initial Insight Generated:
{state["initial_insight"]}

Internal Supporting Evidence:
{supporting_context}

Live Web Evidence:
[WEB SOURCE]: {state["web_context"]}

Internal Contradictory Evidence:
{contradiction_context}

Instructions:
1. Produce a final, balanced insight that leverages both INTERNAL sources and LIVE WEB data.
2. Acknowledge any contradictions within the data.
3. Every claim MUST cite its exact origin using [INTERNAL SOURCE X] or [WEB SOURCE].
4. End with a Confidence Score between 0.0 and 1.0 based on how well-supported the insight is.
5. Format your response as:

VERIFIED INSIGHT:
[Your balanced, attributed insight here]

CONFIDENCE SCORE: [0.0-1.0]

REASONING: [1-2 sentences on why you gave this confidence score]"""

    response = llm.invoke(prompt)
    content = response.content

    # Extract confidence score
    confidence = CONFIDENCE_THRESHOLD
    try:
        for line in content.split("\n"):
            if "CONFIDENCE SCORE:" in line:
                score_str = line.split(":")[-1].strip()
                confidence = float(score_str)
                break
    except Exception:
        confidence = CONFIDENCE_THRESHOLD

    # Build sources list
    sources = []
    for doc in state["retrieved_docs"] + state["contradictions"]:
        source = {
            "title": doc.metadata.get("title", "Unknown Title"),
            "publisher": doc.metadata.get("source", "Unknown"),
            "url": doc.metadata.get("url", doc.page_content)
        }
        if source not in sources:
            sources.append(source)

    # Add Web Enrichment as a visible source if it contains actual data
    web_text = str(state.get("web_context", ""))
    if web_text and len(web_text) > 50:
        if "No live web results retrieved" not in web_text:
            sources.append({
                "title": "Live Internet Enrichment Results (DuckDuckGo)",
                "publisher": "DUCKDUCKGO SEARCH",
                "url": "https://duckduckgo.com"
            })

    flagged = confidence < CONFIDENCE_THRESHOLD

    return {
        **state,
        "final_insight": content,
        "sources": sources,
        "confidence_score": confidence,
        "flagged_for_review": flagged
    }


# --- Build the graph ---
def build_graph():
    workflow = StateGraph(InsightState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_insight_node)
    workflow.add_node("self_correct", self_correct_node)
    workflow.add_node("attribute", attribution_node)

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "web_search")
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", "self_correct")
    workflow.add_edge("self_correct", "attribute")
    workflow.add_edge("attribute", END)

    return workflow.compile()


# --- Main runner ---
def run_pipeline(query: str) -> InsightState:
    graph = build_graph()

    initial_state = InsightState(
        query=query,
        retrieved_docs=[],
        web_context="",
        initial_insight="",
        contradictions=[],
        final_insight="",
        sources=[],
        confidence_score=0.0,
        flagged_for_review=False
    )

    result = graph.invoke(initial_state)
    return result


if __name__ == "__main__":
    query = input("Enter your market intelligence query: ")
    result = run_pipeline(query)
    print("\n" + "=" * 60)
    print(result["final_insight"])
    print(f"\nConfidence: {result['confidence_score']}")
    print(f"Flagged for review: {result['flagged_for_review']}")
    print(f"Sources used: {len(result['sources'])}")
