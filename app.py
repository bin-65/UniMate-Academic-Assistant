import os
import tempfile
import streamlit as st
from connection_checker import check_internet_connection
from rag_engine import RAGEngine
from llm_router import LLMRouter
from tools import generate_mcqs, summarize_knowledge_base, solve_math_problem

st.set_page_config(page_title="UniMate - Academic Assistant", page_icon="🎓", layout="wide")

# Modern, Professional Light Theme CSS
st.markdown("""
<style>
    /* Light Elegant Background */
    .stApp {
        background: #f8fafc;
        color: #0f172a;
    }

    /* Professional Top Banner */
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
        margin-bottom: 2rem;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.3rem;
    }

    .sub-title {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.9;
    }

    /* Cards & Container Styling */
    .status-card {
        background: white;
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }

    /* Custom Primary Buttons */
    .stButton>button {
        width: 100%;
        background: #2563eb !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.2s ease-in-out !important;
    }

    .stButton>button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e2e8f0;
        padding: 6px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 8px;
        color: #475569;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #2563eb !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
st.sidebar.title("⚙️ Knowledge Base Upload")
st.sidebar.markdown("Upload course outlines, lecture slides, or policy PDFs.")
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
    calc_input = st.text_area("Enter problem statement or equation:", height=100, placeholder="e.g., Calculate efficiency of a engine operating between 500K and 300K.")
    
    if st.button("Solve Problem"):
        if not calc_input.strip():
            st.warning("Please enter a problem statement.")
        else:
            with st.spinner("Solving step-by-step..."):
                calc_res = solve_math_problem(calc_input, st.session_state.llm_router, is_online)
                st.markdown("---")
                st.markdown(calc_res)
