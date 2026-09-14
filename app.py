import os
import sys
import streamlit as st

# Ensure root directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_router import LLMRouter
try:
    from rag_engine import RAGEngine
except ImportError:
    RAGEngine = None

# 1. Page Configuration
st.set_page_config(
    page_title="UniMate Academic Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Styling & Background Design
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    /* Card Container Styling */
    div[data-testid="stExpander"], div.stCard {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    /* Custom Title Style */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    /* Status Badge */
    .status-badge-online {
        padding: 8px 16px;
        background-color: rgba(34, 197, 94, 0.15);
        border: 1px solid #22c55e;
        color: #4ade80;
        border-radius: 8px;
        font-weight: 600;
    }
    .status-badge-offline {
        padding: 8px 16px;
        background-color: rgba(234, 179, 8, 0.15);
        border: 1px solid #eab308;
        color: #fde047;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

router = LLMRouter()

# 3. Sidebar Features
with st.sidebar:
    st.title("⚙️ UniMate Controls")
    st.markdown("---")
    
    # Document RAG Section
    st.subheader("📚 Academic RAG Documents")
    uploaded_files = st.file_uploader(
        "Upload Course PDFs / Notes",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files and RAGEngine:
        st.success(f"Uploaded {len(uploaded_files)} document(s)")
    
    st.markdown("---")
    st.subheader("💡 Features Active")
    st.markdown("""
    - ⚡ **Auto-Switching Hybrid Router**
    - 📄 **PDF Vector Search & Retrieval**
    - 🎓 **Academic Subject Specialist Prompting**
    """)
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. Main App Interface
st.markdown('<h1 class="main-title">🎓 UniMate Academic Assistant</h1>', unsafe_allow_html=True)
st.caption("Hybrid Online/Offline AI Assistant for Academic Success")
st.markdown("<br>", unsafe_allow_html=True)

# Connection Status Banner
if router.is_online():
    st.markdown('<div class="status-badge-online">🟢 System Status: Online (Groq API Active)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-badge-offline">🟡 System Status: Offline (Local Engine Fallback Active)</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Session Chat State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Prompt
if prompt := st.chat_input("Ask UniMate anything or analyze uploaded documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response, mode_tag = router.get_response(prompt)
        full_response = f"{response}\n\n`{mode_tag}`"
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
