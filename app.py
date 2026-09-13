import os
import tempfile
import streamlit as st
from connection_checker import check_internet_connection
from rag_engine import RAGEngine
from llm_router import LLMRouter
from tools import generate_mcqs, summarize_knowledge_base, solve_math_problem

st.set_page_config(page_title="UniMate - Academic Assistant", page_icon="🎓", layout="wide")

# Sky Blue Background with Watermark Pattern & High Contrast UI
st.markdown("""
<style>
    /* Sky Blue Theme with Watermark Pattern */
    .stApp {
        background-color: #e0f2fe;
        background-image: 
            radial-gradient(#bae6fd 1.5px, transparent 1.5px), 
            linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%);
        background-size: 30px 30px, 100% 100%;
        color: #0f172a;
    }

    /* Academic Watermark Overlay */
    .stApp::before {
        content: "🎓 UNIMATE ACADEMIC ASSISTANT   🎓 UNIMATE ACADEMIC ASSISTANT   🎓 UNIMATE ACADEMIC ASSISTANT";
        position: fixed;
        top: 0;
        left: 0;
        width: 200%;
        height: 200%;
        font-size: 1.8rem;
        font-weight: 900;
        color: rgba(2, 132, 199, 0.04);
        transform: rotate(-15deg);
        pointer-events: none;
        z-index: 0;
        line-height: 120px;
        word-spacing: 50px;
        white-space: wrap;
    }

    /* Main Header Banner */
    .main-header {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 2.2rem 1.5rem;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(2, 132, 199, 0.25);
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }

    .sub-title {
        font-size: 1.15rem;
        font-weight: 400;
        opacity: 0.95;
    }

    /* Custom Primary Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #0284c7, #0369a1) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.2rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
        transition: all 0.2s ease-in-out !important;
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #0369a1, #075985) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45);
    }

    /* Input Box Cards */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #93c5fd !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-size: 1rem !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 10px rgba(2, 132, 199, 0.3) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #cbd5e1;
        padding: 6px;
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 10px;
        color: #334155;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0284c7 !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #f0f9ff !important;
        border-right: 2px solid #bae6fd !important;
    }
</style>
""", unsafe_allow_html=True)

# Main Banner
st.markdown("""
<div class="main-header">
    <div class="main-title">🎓 UniMate</div>
    <div class="sub-title">Hybrid Offline-Online RAG-Based AI Academic Assistant</div>
</div>
""", unsafe_allow_html=True)

# Persistent Engine Initialization
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
if "llm_router" not in st.session_state:
    st.session_state.llm_router = LLMRouter()

# System Connectivity Check
is_online = check_internet_connection()

# Status Dashboard Cards
col1, col2, col3 = st.columns(3)
with col1:
    if is_online:
        st.success("● AI Engine: Online (Groq Cloud Active)")
    else:
        st.warning("● AI Engine: Offline (Local Ollama Active)")
with col2:
    kb_loaded = st.session_state.rag_engine.vector_store is not None
    st.info(f"📚 Knowledge Base: {'Loaded' if kb_loaded else 'Empty'}")
with col3:
    st.success("🔒 Strict No-Guessing Mode: Active")

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar - Document Indexing
st.sidebar.title("⚙️ Knowledge Base Setup")
st.sidebar.markdown("Upload department course outlines or policy PDFs.")
uploaded_files = st.sidebar.file_uploader("Select PDF Documents", type=["pdf"], accept_multiple_files=True)

if st.sidebar.button("Build / Update Index"):
    if uploaded_files:
        temp_paths = []
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.getvalue())
                temp_paths.append(tmp.name)
        
        with st.spinner("Indexing documents into FAISS vector space..."):
            chunks_count = st.session_state.rag_engine.process_and_index_pdfs(temp_paths)
            for path in temp_paths:
                os.remove(path)
            st.sidebar.success(f"Indexed {chunks_count} chunks successfully!")
            st.rerun()
    else:
        st.sidebar.error("Please upload at least one PDF file.")

# Main Interactive Feature Tabs
tab_qa, tab_mcq, tab_summary, tab_calc = st.tabs([
    "💬 Ask Academic Question", 
    "📝 MCQ Generator", 
    "📑 Document Summarizer", 
    "🧮 Step-by-Step Calculator"
])

# --- Tab 1: Q/A ---
with tab_qa:
    st.subheader("Ask Anything From Your Study Material")
    user_query = st.text_area("Type your question here (Supports both English and Urdu):", height=120, placeholder="e.g., What are the core topics covered in chapter 2?")
    
    if st.button("Ask UniMate"):
        if not user_query.strip():
            st.warning("Please type a valid question.")
        else:
            with st.spinner("Analyzing documents & generating response..."):
                context, sources = st.session_state.rag_engine.retrieve_context(user_query)
                response, engine_used = st.session_state.llm_router.query(user_query, context, is_online)
                
                st.markdown("---")
                st.markdown("### Answer")
                st.markdown(response)
                st.caption(f"⚡ Processing Engine: **{engine_used}**")
                
                if sources:
                    st.markdown("#### 📚 Verified Sources:")
                    for src in sources:
                        st.markdown(f"- `{src}`")

# --- Tab 2: MCQ Generator ---
with tab_mcq:
    st.subheader("Practice Quiz & MCQ Generator")
    st.markdown("Generate practice multiple choice questions directly from your indexed PDFs.")
    num_q = st.slider("Select Number of Questions", min_value=1, max_value=10, value=3)
    
    if st.button("Generate MCQs"):
        if not st.session_state.rag_engine.vector_store:
            st.warning("Please upload and index PDF documents first in the sidebar.")
        else:
            with st.spinner("Generating quiz questions..."):
                mcq_res = generate_mcqs(st.session_state.rag_engine, st.session_state.llm_router, is_online, num_q)
                st.markdown("---")
                st.markdown(mcq_res)

# --- Tab 3: Summarizer ---
with tab_summary:
    st.subheader("Academic Document Summarizer")
    st.markdown("Get a structured summary of core concepts from your uploaded study materials.")
    
    if st.button("Generate Summary"):
        if not st.session_state.rag_engine.vector_store:
            st.warning("Please upload and index PDF documents first in the sidebar.")
        else:
            with st.spinner("Synthesizing document summary..."):
                summary_res = summarize_knowledge_base(st.session_state.rag_engine, st.session_state.llm_router, is_online)
                st.markdown("---")
                st.markdown(summary_res)

# --- Tab 4: Calculator ---
with tab_calc:
    st.subheader("Step-by-Step Academic Problem Solver")
    st.markdown("Solve mathematical, engineering, or logical problems with full formula steps.")
    calc_input = st.text_area("Enter problem statement or equation:", height=100, placeholder="e.g., Calculate efficiency of a heat engine operating between 500K and 300K.")
    
    if st.button("Solve Problem"):
        if not calc_input.strip():
            st.warning("Please enter a problem statement.")
        else:
            with st.spinner("Solving step-by-step..."):
                calc_res = solve_math_problem(calc_input, st.session_state.llm_router, is_online)
                st.markdown("---")
                st.markdown(calc_res)
