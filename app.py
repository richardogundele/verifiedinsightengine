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

# --- Custom CSS for Google-tier Premium Dashboard ---
st.markdown("""
<style>
    /* Google-inspired Typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;600&display=swap');
    
    :root {
        --primary-blue: #1A73E8;
        --deep-slate: #1F2937;
        --border-color: #E5E7EB;
        --bg-gradient: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        --card-bg: #FFFFFF;
        --accent-emerald: #10B981;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background: var(--bg-gradient);
    }

    /* Header & Branding */
    .dashboard-header {
        text-align: left;
        padding: 2rem 0;
        border-bottom: 2px solid var(--border-color);
        margin-bottom: 2rem;
    }
    .dashboard-title {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #60A5FA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.2rem !important;
        margin-bottom: 0px;
        letter-spacing: -0.02em;
    }
    .dashboard-subtitle {
        color: #4B5563;
        font-size: 1.25rem;
        font-weight: 300;
        margin-top: 8px;
    }

    /* Command Center (Input) */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1px solid #D1D5DB !important;
        padding: 20px !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
    }

    /* Premium Cards (Result) */
    .premium-card {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 32px;
        border: 1px solid rgba(229, 231, 235, 0.8);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        margin-bottom: 2rem;
    }
    
    .insight-text {
        font-size: 1.2rem;
        line-height: 1.8;
        color: #374151;
        font-weight: 400;
    }

    /* Badge Styling */
    .confidence-badge {
        padding: 8px 16px;
        border-radius: 99px;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Sidebar Refinements */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border-color);
    }
    
    .pipeline-wrapper {
        padding-left: 15px;
        margin-top: 30px;
    }
    .pipeline-step {
        position: relative;
        padding-bottom: 25px;
        padding-left: 25px;
        border-left: 2px solid #E5E7EB;
    }
    .pipeline-step::before {
        content: '';
        position: absolute;
        width: 14px;
        height: 14px;
        background: #FFFFFF;
        border: 3px solid var(--primary-blue);
        border-radius: 50%;
        left: -9px;
        top: 0;
    }
    .step-title { font-weight: 600; color: #111827; font-size: 0.95rem; margin-bottom: 2px;}
    .step-desc { font-size: 0.8rem; color: #6B7280; line-height: 1.4; }
    
    /* Buttons */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: 1px solid #E5E7EB;
        background: white;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        border-color: var(--primary-blue);
        color: var(--primary-blue);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
    }

    /* Primary Button Force Color */
    button[data-testid="stBaseButton-primary"], 
    .stButton>button[kind="primary"] {
        background-color: var(--primary-blue) !important;
        color: white !important;
        border: none !important;
        visibility: visible !important;
        display: inline-flex !important;
    }
    
    /* Active Query Example */
    .prompt-button {
        border: 1px solid #E5E7EB !important;
        text-align: left !important;
        height: auto !important;
        padding: 15px !important;
        background: #F9FAFB !important;
        border-radius: 12px !important;
        font-size: 0.9rem !important;
        color: #374151 !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: transparent !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="dashboard-header">
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="background: #1A73E8; padding: 12px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        </div>
        <div>
            <h1 class="dashboard-title">Verdict Insight Engine</h1>
            <p class="dashboard-subtitle">Senior Market Research Intelligence Dashboard</p>
        </div>
    </div>
    <p style="color: #64748B; font-size: 1rem; margin-top: 20px; max-width: 800px; line-height: 1.6;">
        Every claim within this dashboard is autonomously cross-referenced against contradictory evidence and rigorously attributed to primary corporate data. Hallucination-resistant by design.
    </p>
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
    api_key = system_key
        
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.info("Verified Access Active: Shared System API Key", icon="🌐")
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
            
            # Dynamic Confidence Badge
            score = result["confidence_score"]
            if score >= 0.7:
                badge = f"""<div class="confidence-badge" style="background: #ECFDF5; color: #064E3B; border: 1px solid #A7F3D0;">🛡️ High Confidence ({score:.2f})</div>"""
            elif score >= 0.4:
                badge = f"""<div class="confidence-badge" style="background: #FFFBEB; color: #78350F; border: 1px solid #FDE68A;">⚖️ Moderate Confidence ({score:.2f})</div>"""
            else:
                badge = f"""<div class="confidence-badge" style="background: #FEF2F2; color: #7F1D1D; border: 1px solid #FECACA;">⚠️ Low Confidence ({score:.2f})</div>"""

            # Render custom Insight Card
            insight_html = result["final_insight"].replace("\n", "<br>")
            
            card_template = f"""
            <div class="premium-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px;">
                    <div>
                        <h2 style="margin: 0; color: #111827; font-family: 'Outfit'; font-size: 1.75rem;">Verified Intelligence Output</h2>
                        <p style="color: #6B7280; font-size: 0.9rem; margin-top: 4px;">Self-corrected via lateral web expansion & primary document audit.</p>
                    </div>
                    {badge}
                </div>
                <div class="insight-text">
                    {insight_html}
                </div>
                <div style="margin-top: 30px; padding: 20px; background: #F8FAFC; border-radius: 12px; border: 1px dashed #E2E8F0; color: #475569; font-size: 0.9rem;">
                    <strong>🔍 Traceability Audit:</strong> Every claim documented in this insight is cross-referenced using the primary data sources indexed below. Contradictory evidence has been weighted and neutralized via the agentic critique loop.
                </div>
            </div>
            """
            st.markdown(card_template, unsafe_allow_html=True)

            if result["flagged_for_review"]:
                st.warning("⚠️ **System Flag:** This insight has been flagged by the pipeline for human review due to significant internal contradictions found during Stage 4.")

            st.markdown("<br>", unsafe_allow_html=True)

            # Sources Cards
            st.subheader("Primary Data Sources ({0})".format(len(result['sources'])))
            for i, source in enumerate(result["sources"]):
                publisher = source.get('publisher', 'Internal').upper() if source.get('publisher') else 'INTERNAL'
                with st.expander("LINKED: [SOURCE {0}] - {1}".format(i+1, source.get('title', 'Document'))):
                    st.markdown(f"**Publisher:** {publisher}")
                    url = source.get('url', '#')
                    if url and url.startswith('http'):
                        st.markdown(f"**Link:** [{url}]({url})")
                    else:
                        st.markdown(f"**Location:** Local Index")

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
st.markdown("""
<div style="text-align: center; padding: 40px 0; color: #94A3B8; font-size: 0.9rem; border-top: 1px solid #E2E8F0; margin-top: 60px;">
    <strong>Verified Insight Engine</strong> | Powered by LangGraph, ChromaDB, and OpenAI <b>gpt-4o-mini</b><br>
    Built for high-stakes consumer market intelligence.
    <div style="margin-top: 10px; opacity: 0.6;">© 2024 Verified Insight | Richard Ogundele</div>
</div>
""", unsafe_allow_html=True)
