"""  Streamlit frontend for the Verified Insight Engine.   """

import os
import streamlit as st
from dotenv import load_dotenv
from graph import run_pipeline

# Load environment variables (from .env if it exists)
load_dotenv()

# --- Page config ---
st.set_page_config(
    page_title="Verified Insight Engine",
    page_icon="🔍",
    layout="wide"
)

# --- Custom CSS injected for Premium Dashboard UI ---
st.markdown("""
<style>
    /* Global Typography & Spacing */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Header Styling */
    .dashboard-header {
        text-align: center;
        padding-bottom: 2rem;
    }
    .dashboard-title {
        background: -webkit-linear-gradient(45deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        margin-bottom: 0px;
    }
    .dashboard-subtitle {
        color: #4B5563;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 5px;
    }

    /* Cards */
    .premium-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    
    .insight-text {
        font-size: 1.15rem;
        line-height: 1.7;
        color: #1F2937;
    }

    /* Pipeline Visual Stepper (Sidebar) */
    .pipeline-wrapper {
        border-left: 2px solid #E5E7EB;
        padding-left: 20px;
        margin-left: 10px;
        margin-top: 20px;
    }
    .pipeline-step {
        position: relative;
        margin-bottom: 25px;
    }
    .pipeline-step::before {
        content: '';
        position: absolute;
        width: 12px;
        height: 12px;
        background: #3B82F6;
        border-radius: 50%;
        left: -27px;
        top: 5px;
        box-shadow: 0 0 0 4px #EFF6FF;
    }
    .step-title { font-weight: 600; color: #111827; margin-bottom: 2px;}
    .step-desc { font-size: 0.85rem; color: #6B7280; }
    
    /* Button Override */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">Verdict Insight Engine</h1>
    <p class="dashboard-subtitle">Proactive Market Research Agent & Agentic RAG Pipeline</p>
    <p style="color: #6B7280; font-size: 0.95rem;"><em>Every insight is self-corrected against contradictory evidence and rigorously attributed to primary corporate data.</em></p>
</div>
""", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("⚙️ Architecture")
    st.caption("*The LLM acts purely as a plug-in semantic processor.*")

    # Visual Pipeline representation
    st.markdown("""
    <div class="pipeline-wrapper">
        <div class="pipeline-step">
            <div class="step-title">1. Ingest</div>
            <div class="step-desc">Structured aggregation (PDFs, Web)</div>
        </div>
        <div class="pipeline-step" style="opacity: 0.6;">
            <div class="step-title">2. Enrich (Planned)</div>
            <div class="step-desc">Proactive lateral expansion</div>
        </div>
        <div class="pipeline-step">
            <div class="step-title">3. Retrieve & Search</div>
            <div class="step-desc">Vector DB + Live Web Data</div>
        </div>
        <div class="pipeline-step">
            <div class="step-title">4. Generate & Critique</div>
            <div class="step-desc">Self-correcting contradiction loops</div>
        </div>
        <div class="pipeline-step">
            <div class="step-title">5. Attribute</div>
            <div class="step-desc">Rigid mapping to primary sources</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🧬 Active Data Assets")
    st.markdown("""
    *The pipeline is currently pulling from:*
    - [UNICEF Reports: Digital Childhoods](https://www.unicef.org/reports/digital-childhood-geographic-and-developmental-perspectives)
    - [Ofcom 2024/25: Children's Media Use](https://www.ofcom.org.uk/research-and-data/media-literacy-research/childrens/children-and-parents-media-use-and-attitudes-report-2024)
    - [Alan Turing Institute: AI Governance](https://www.turing.ac.uk/research/publications)
    - [Live Web Enrichment (DuckDuckGo)](https://duckduckgo.com)
    """)

    st.markdown("""
    **Verification Thresholds:**
    - [High] 0.7+ = Statistically sound
    - [Moderate] 0.4-0.69 = Review recommended
    - [Low] Below 0.4 = Flagged (requires human analyst review)
    """)

    st.divider()
    
    # Check for existing system key
    system_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    
    # Secure API Key input
    api_key_input = st.text_input(
        "OpenAI API Key (Override)", 
        type="password", 
        placeholder="sk-..." if not system_key else "System key active (Click to override)", 
        help="Paste your own OpenAI key here to override the system key. Use this if you have your own credits."
    )
    
    # Final API key to use
    api_key = api_key_input if api_key_input else system_key
        
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        if api_key_input:
            st.success("Using provided User API Key", icon="👤")
        elif system_key:
            st.info("Using Shared System API Key", icon="🌐")
    else:
        st.warning("No API Key found. Results will not be generated.", icon="⚠️")

    st.divider()
    st.markdown("**LLM Socket:** gpt-4o-mini (OpenAI API)")
    st.markdown("**Vector Store:** ChromaDB")
    st.markdown("**Ingestion:** Custom Web/PDF Scrapers")
    st.markdown("**Built by:** Richard Ogundele")

# --- Example queries ---
st.subheader("💡 Proactive Intelligence Queries")
examples = [
    "Identify cross-category purchasing behaviours for families with children aged 3-18.",
    "What are the psychographic personality types of children with heavy screen time?",
    "How has parental monitoring of YouTube and TikTok changed since 2022?",
    "What are the emerging trends in digital literacy and Trustworthy AI?"
]

cols = st.columns(2)
selected_example = None
for i, example in enumerate(examples):
    if cols[i % 2].button(example, use_container_width=True):
        selected_example = example

st.divider()

# --- Query input ---
st.subheader("Deep Segmentation Search")
query = st.text_area(
    label="Enter your market intelligence question (e.g., target tracking, behavioral shifts, deep segmentation):",
    value=selected_example if selected_example else "",
    height=80,
    placeholder="e.g. Determine the lateral psychographic trends and social media preferences for..."
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

        status.text("Stage 1/5: Retrieving internal corporate documents...")
        progress_bar.progress(20)

        try:
            result = run_pipeline(query)
            
            status.text("Stage 2/5: Querying live internet (DuckDuckGo)...")
            progress_bar.progress(40)
            
            status.text("Stage 3/5: Generating initial insight...")
            progress_bar.progress(60)
            
            status.text("Stage 4/5: Self-correcting against contradictions...")
            progress_bar.progress(80)
            
            status.text("Stage 5/5: Attributing claims...")
            progress_bar.progress(100)
            status.empty()

            # --- Results ---
            st.divider()
            
            score = result["confidence_score"]
            if score >= 0.7:
                badge = """<div style="background-color: #ECFDF5; color: #065F46; padding: 6px 12px; border-radius: 9999px; display: inline-block; font-weight: 600; font-size: 0.9rem; border: 1px solid #A7F3D0;">High Confidence (""" + f"{score:.2f}" + """)</div>"""
            elif score >= 0.4:
                badge = """<div style="background-color: #FFFBEB; color: #92400E; padding: 6px 12px; border-radius: 9999px; display: inline-block; font-weight: 600; font-size: 0.9rem; border: 1px solid #FDE68A;">Moderate Confidence (""" + f"{score:.2f}" + """) - Review Advised</div>"""
            else:
                badge = """<div style="background-color: #FEF2F2; color: #991B1B; padding: 6px 12px; border-radius: 9999px; display: inline-block; font-weight: 600; font-size: 0.9rem; border: 1px solid #FECACA;">Low Confidence (""" + f"{score:.2f}" + """) - Flagged for Analyst Review</div>"""

            # Render custom Insight Card
            insight_html = result["final_insight"].replace("\n", "<br>")
            
            card_template = """
            <div class="premium-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #E5E7EB; padding-bottom: 15px;">
                    <h2 style="margin: 0; color: #111827;">Verified Insight</h2>
                    {badge_placeholder}
                </div>
                <div class="insight-text">
                    {insight_placeholder}
                </div>
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed #E5E7EB; color: #6B7280; font-size: 0.85rem; font-style: italic;">
                    *Transparency Note: Every claim above is cited to a specific internal document or live web source. Use the "Primary Data Sources" section below to audit the full source metadata.*
                </div>
            </div>
            """
            st.markdown(card_template.replace("{badge_placeholder}", badge).replace("{insight_placeholder}", insight_html), unsafe_allow_html=True)

            if result["flagged_for_review"]:
                st.warning("⚠️ **System Flag:** This insight has been flagged by the pipeline for human review due to significant internal contradictions found during Stage 4.")

            st.markdown("<br>", unsafe_allow_html=True)

            # Sources Cards
            st.subheader("Primary Data Sources ({0})".format(len(result['sources'])))
            for i, source in enumerate(result["sources"]):
                with st.expander("LINKED: [INTERNAL SOURCE {0}] - {1}".format(i+1, source['title'])):
                    st.markdown(f"**Publisher:** {source['publisher'].upper()}")
                    if source['url'].startswith('http'):
                        st.markdown(f"**Link:** [{source['url']}]({source['url']})")
                    else:
                        st.markdown(f"**Location:** {source['url']}")

            # Pipeline trace
            with st.expander("Pipeline trace - Initial insight (before self-correction)"):
                st.markdown("**Initial insight generated before contradiction check:**")
                st.markdown(result["initial_insight"])
                
                st.markdown("---")
                st.markdown("**Live Web Data Retrieved:**")
                st.info(result.get("web_context", "None found."))

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
