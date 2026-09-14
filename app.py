import os
import sys
import streamlit as st

# Path configuration
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

# 2. Light Professional Theme with Full Screen Library Watermark Pattern
st.markdown("""
    <style>
    /* Global Light Professional Theme */
    html, body, .stApp {
        background-color: #f1f5f9 !important;
        /* Full Screen Repeatable Library & Study SVG Watermark Pattern */
        background-image: 
            linear-gradient(135deg, rgba(248, 250, 252, 0.82) 0%, rgba(226, 232, 240, 0.85) 100%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Cg fill='%23475569' fill-opacity='0.12'%3E%3Cpath d='M10 25h12v65H10zM25 35h10v55H25zM38 18h14v72H38zM55 40h8v50h-8zM66 28h12v62H66zM81 20h14v70H81zM98 32h10v58H98z'/%3E%3Ccircle cx='30' cy='15' r='5'/%3E%3Cpath d='M60 10l10 12H50z'/%3E%3C/g%3E%3C/svg%3E") !important;
        background-repeat: repeat !important;
        background-attachment: fixed !important;
        background-size: 140px 140px !important;
        color: #0f172a !important;
    }

    /* Soft Glassmorphism Cards */
    div[data-testid="stExpander"], div.stCard, section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.88) !important;
        border: 1px solid rgba(203, 213, 225, 0.9) !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04) !important;
    }

    /* Sidebar Background Integration */
    section[data-testid="stSidebar"] {
        background-color: rgba(248, 250, 252, 0.92) !important;
    }

    /* Professional Soft Typography */
    .main-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.1rem;
        letter-spacing: -0.5px;
    }

    .sub-title {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    /* Status Badges - Light Soft Colors */
    .status-badge-online {
        padding: 8px 18px;
        background-color: #dcfce7;
        border: 1px solid #86efac;
        color: #15803d;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-offline {
        padding: 8px 18px;
        background-color: #fef9c3;
        border: 1px solid #fde047;
        color: #a16207;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

router = LLMRouter()

# 3. Sidebar Controls & Academic Multi-Tools
with st.sidebar:
    st.title("⚙️ UniMate Controls")
    st.markdown("---")
    
    # Tool Selector
    st.subheader("🎯 Academic Tools")
    selected_tool = st.selectbox(
        "Select Mode / Feature",
        [
            "💬 General Assistant Chat",
            "📝 Quiz & MCQ Generator",
            "📖 Lecture & Note Summarizer",
            "🧮 Math & Logic Problem Solver"
        ]
    )
    
    st.markdown("---")
    
    # Document RAG Upload Section
    st.subheader("📚 Library Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload Course PDFs / Notes",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"Loaded {len(uploaded_files)} PDF document(s)")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. Main App Interface Header
st.markdown('<h1 class="main-title">🎓 UniMate Academic Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Hybrid Smart Learning Engine for Academic Success</p>', unsafe_allow_html=True)

# Connection Badge
if router.is_online():
    st.markdown('<div class="status-badge-online">🟢 System Status: Online (Groq Engine Active)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-badge-offline">🟡 System Status: Offline (Local Engine Active)</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. Session State Initializer
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Interactive Prompt Handling with Dynamic Tool Prompting
if prompt := st.chat_input("Ask a question, generate quiz, or summarize notes..."):
    
    # Feature Prompt Routing
    final_prompt = prompt
    if selected_tool == "📝 Quiz & MCQ Generator":
        final_prompt = f"Create a practice quiz with 5 Multiple Choice Questions (MCQs) and detailed answers for: {prompt}"
    elif selected_tool == "📖 Lecture & Note Summarizer":
        final_prompt = f"Provide a clean, structured summary with key points for the following content: {prompt}"
    elif selected_tool == "🧮 Math & Logic Problem Solver":
        final_prompt = f"Solve this math/logic problem step-by-step with clear explanations: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response, mode_tag = router.get_response(final_prompt)
        full_response = f"{response}\n\n`{mode_tag}`"
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
