"""  Streamlit frontend for the Verified Insight Engine.   """

import os
import streamlit as st
from graph import run_pipeline

# --- Page config ---
st.set_page_config(
    page_title="Verified Insight Engine",
    page_icon="🔍",
    layout="wide"
)

# --- Header ---
st.title("🔍 Verified Insight Engine")
st.markdown(
    "**Agentic RAG system with self-correcting attribution loops for family and consumer market intelligence.**"
)
st.markdown(
    "_Every insight is verified against contradictory evidence and attributed to source documents. "
    "All processing runs locally - no data leaves your machine._"
)
st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("ℹ️ How it works")
    st.markdown("""
    **4-stage agentic pipeline:**

    1. **Retrieve** - semantic search across ingested documents
    2. **Generate** - LLM produces initial insight with citations
    3. **Self-Correct** - agent searches for contradictory evidence
    4. **Attribute** - every claim mapped to a source document

    **Confidence scoring:**
    - 🟢 0.7+ = High confidence
    - 🟡 0.4-0.69 = Moderate - review recommended
    - 🔴 Below 0.4 = Flagged for human review

    **Privacy:** Powered by OpenAI models.
    """)

    st.divider()
    
    # Secure API Key input
    api_key_input = st.text_input(
        "OpenAI API Key (Required for app to run)", 
        type="password", 
        placeholder="sk-...", 
        help="You can also set this in Streamlit Community Cloud Secrets."
    )
    
    # Use key from Streamlit secrets if available, otherwise from input
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", api_key_input)
    except Exception:
        api_key = api_key_input
        
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    st.divider()
    st.markdown("**Model:** gpt-4o-mini via OpenAI")
    st.markdown("**Vector store:** ChromaDB")
    st.markdown("**Built by:** Richard Ogundele")

# --- Example queries ---
st.subheader("Try an example query")
examples = [
    "How has screen time among children aged 5-10 changed in recent years?",
    "What are the key trends in family media consumption habits?",
    "How do parents make purchasing decisions for children's products?",
    "What role does social media play in influencing Gen Alpha behaviour?"
]

cols = st.columns(2)
selected_example = None
for i, example in enumerate(examples):
    if cols[i % 2].button(example, use_container_width=True):
        selected_example = example

st.divider()

# --- Query input ---
st.subheader("Your query")
query = st.text_area(
    label="Enter your market intelligence question:",
    value=selected_example if selected_example else "",
    height=80,
    placeholder="e.g. What are the key trends in children's digital media consumption?"
)

run_button = st.button("🚀 Run Verified Insight", type="primary", use_container_width=True)

if run_button and not os.environ.get("OPENAI_API_KEY"):
    st.error("Please provide an OpenAI API Key in the sidebar to run the pipeline.")
    st.stop()

# --- Run pipeline ---
if run_button and query.strip():
    with st.spinner("Running agentic pipeline... this may take 30-60 seconds on first run."):

        # Progress indicators
        progress_bar = st.progress(0)
        status = st.empty()

        status.text("Stage 1/4: Retrieving relevant documents...")
        progress_bar.progress(25)

        try:
            result = run_pipeline(query)
            progress_bar.progress(100)
            status.empty()

            # --- Results ---
            st.divider()
            st.subheader("📊 Verified Insight")

            # Confidence badge
            score = result["confidence_score"]
            if score >= 0.7:
                st.success(f"✅ Confidence Score: {score:.2f} - High confidence insight")
            elif score >= 0.4:
                st.warning(f"⚠️ Confidence Score: {score:.2f} - Moderate confidence - human review recommended")
            else:
                st.error(f"🔴 Confidence Score: {score:.2f} - Low confidence - flagged for human review")

            if result["flagged_for_review"]:
                st.warning("⚠️ This insight has been flagged for human review due to low confidence or significant contradictions.")

            # Main insight
            st.markdown(result["final_insight"])

            st.divider()

            # Sources
            st.subheader(f"📚 Sources Used ({len(result['sources'])})")
            for i, source in enumerate(result["sources"]):
                with st.expander(f"[source {i+1}]: {source['title']}"):
                    st.markdown(f"**Publisher:** {source['publisher'].upper()}")
                    if source['url'].startswith('http'):
                        st.markdown(f"**Link:** [{source['url']}]({source['url']})")
                    else:
                        st.markdown(f"**Location:** {source['url']}")

            # Pipeline trace
            with st.expander("🔬 Pipeline trace - Initial insight (before self-correction)"):
                st.markdown("**Initial insight generated before contradiction check:**")
                st.markdown(result["initial_insight"])

                if result["contradictions"]:
                    st.markdown(f"**Contradictory documents found:** {len(result['contradictions'])}")
                    for i, doc in enumerate(result["contradictions"]):
                        st.markdown(f"_Contra {i+1}: {doc.page_content[:200]}..._")

        except Exception as e:
            progress_bar.empty()
            status.empty()
            st.error(f"Pipeline error: {str(e)}")
            st.markdown("**Troubleshooting:**")
            st.markdown("- Verify your OpenAI API Key is entered correctly and has valid billing.")
            st.markdown("- Check if you need to run `python ingest.py` to ingest documents via OpenAI models.")

elif run_button and not query.strip():
    st.warning("Please enter a query before running.")

# --- Footer ---
st.divider()
st.caption(
    "Verified Insight Engine | Built with LangChain, LangGraph, ChromaDB, OpenAI | "
)
