import os
import tempfile
import streamlit as st
from connection_checker import check_internet_connection
from rag_engine import RAGEngine
from llm_router import LLMRouter

st.set_page_config(page_title="UniMate - Academic Assistant", page_icon="🎓", layout="wide")

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
if "llm_router" not in st.session_state:
    st.session_state.llm_router = LLMRouter()

st.markdown("<h1 style='text-align: center;'>🎓 UniMate</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Hybrid Offline-Online RAG-Based AI Academic Assistant</h4>", unsafe_allow_html=True)
st.divider()

is_online = check_internet_connection()

col1, col2, col3 = st.columns(3)
with col1:
    if is_online:
        st.success("● Network: Online (Groq Active)")
    else:
        st.warning("● Network: Offline (Local AI Active)")
with col2:
    kb_loaded = st.session_state.rag_engine.vector_store is not None
    st.info(f"📚 Knowledge Base: {'Loaded' if kb_loaded else 'Empty'}")
with col3:
    st.success("🔒 No-Guessing Mode: Active")

st.divider()

st.sidebar.title("🛠️ Knowledge Base Setup")
uploaded_files = st.sidebar.file_uploader("Upload Department PDFs", type=["pdf"], accept_multiple_files=True)

if st.sidebar.button("Build / Update Index"):
    if uploaded_files:
        temp_paths = []
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.getvalue())
                temp_paths.append(tmp.name)
        
        with st.spinner("Processing document embeddings..."):
            chunks_count = st.session_state.rag_engine.process_and_index_pdfs(temp_paths)
            for path in temp_paths:
                os.remove(path)
            st.sidebar.success(f"Indexed {chunks_count} chunks successfully!")
            st.rerun()
    else:
        st.sidebar.error("Please select PDF files first.")

st.subheader("💬 Ask Your Academic Question")
user_query = st.text_area("Type your question here (Supports English & Urdu):", height=100)

if st.button("Ask UniMate", type="primary"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            context, sources = st.session_state.rag_engine.retrieve_context(user_query)
            response, engine_used = st.session_state.llm_router.query(user_query, context, is_online)
            
            st.markdown("### Answer")
            st.write(response)
            st.caption(f"Engine Executed: **{engine_used}**")
            
            if sources:
                st.markdown("#### Trusted Sources")
                for src in sources:
                    st.markdown(f"- `{src}`")
