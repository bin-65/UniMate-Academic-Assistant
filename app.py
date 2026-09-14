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

# 2. Light Professional Theme with Full Library Watermark Background
st.markdown("""
    <style>
    /* Full Page Light Professional Background with Library/Books Watermark */
    .stApp {
        background-color: #f8fafc;
        background-image: 
            linear-gradient(135deg, rgba(241, 245, 249, 0.85) 0%, rgba(224, 231, 255, 0.7) 100%),
            url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 20h8v40h-8zM22 25h8v35h-8zM32 15h8v45h-8zM42 30h8v30h-8zM52 18h8v42h-8zM62 22h8v38h-8z' fill='%2364748b' fill-opacity='0.12'/%3E%3C/svg%3E");
        background-repeat: repeat;
        color: #1e293b;
    }

    /* Light Glassmorphism Card Panels */
    div[data-testid="stExpander"], div.stCard, section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(203, 213, 225, 0.8) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Soft Professional Title */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.1rem;
    }

    .sub-title {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* Status Badges - Light Soft Pastel Colors */
    .status-badge-online {
        padding: 8px 16px;
        background-color: #dcfce7;
        border: 1px solid #86efac;
        color: #166534;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-offline {
        padding: 8px 16px;
        background-color: #fef9c3;
        border: 1px solid #fde047;
        color: #854d0e;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

router = LLMRouter()

# 3. Sidebar Controls & Academic Tools
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
    
    # Document RAG Upload
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

# 4. Main Interface Header
st.markdown('<h1 class="main-title">🎓 UniMate Academic Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Hybrid Smart Learning Engine for Academic Success</p>', unsafe_allow_html=True)

# Connection Status Badge
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

# 6. Interactive Prompt Handling
if prompt := st.chat_input("Ask a question, generate quiz, or summarize notes..."):
    
    # Feature Prompt Routing
    final_prompt = prompt
    if selected_tool == "📝 Quiz & MCQ Generator":
        final_prompt = f"Create a practice quiz with 5 Multiple Choice Questions (MCQs) and answers for: {prompt}"
    elif selected_tool == "📖 Lecture & Note Summarizer":
        final_prompt = f"Provide a structured summary with key points for: {prompt}"
    elif selected_tool == "🧮 Math & Logic Problem Solver":
        final_prompt = f"Solve this math/logic problem step-by-step: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response, mode_tag = router.get_response(final_prompt)
        full_response = f"{response}\n\n`{mode_tag}`"
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
