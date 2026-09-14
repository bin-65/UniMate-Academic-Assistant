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

# 2. Custom CSS with Background Watermark & Academic Theme
st.markdown("""
    <style>
    /* Dark Academic Theme Background with Watermark SVG Pattern */
    .stApp {
        background-color: #0f172a;
        background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 0),
                          url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M20 20h10v60H20zM35 30h10v50H35zM50 15h10v65H50zM65 25h10v55H65zM80 35h10v45H80z' fill='%23ffffff' fill-opacity='0.02'/%3E%3C/svg%3E");
        background-size: 24px 24px, 200px 200px;
        color: #f8fafc;
    }
    
    /* Card Glassmorphism Effect */
    div[data-testid="stExpander"], div.stCard {
        background-color: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        backdrop-filter: blur(8px);
    }

    /* Main Title Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    /* Status Badges */
    .status-badge-online {
        padding: 8px 16px;
        background-color: rgba(34, 197, 94, 0.15);
        border: 1px solid #22c55e;
        color: #4ade80;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-offline {
        padding: 8px 16px;
        background-color: rgba(234, 179, 8, 0.15);
        border: 1px solid #eab308;
        color: #fde047;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

router = LLMRouter()

# 3. Sidebar Controls & Multi-Feature Hub
with st.sidebar:
    st.title("⚙️ UniMate Academic Hub")
    st.markdown("---")
    
    # Feature 1: Academic Tool Selector
    st.subheader("🎯 Academic Tools")
    selected_tool = st.selectbox(
        "Select Mode / Tool",
        [
            "💬 General Assistant Chat",
            "📝 Quiz & MCQ Generator",
            "📖 Lecture & Note Summarizer",
            "🧮 Math & Logic Problem Solver"
        ]
    )
    
    st.markdown("---")
    
    # Feature 2: PDF RAG Upload
    st.subheader("📚 RAG Knowledge Base")
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
st.caption("Hybrid Smart Learning Engine for Academic Success")
st.markdown("<br>", unsafe_allow_html=True)

# Connection Badge
if router.is_online():
    st.markdown('<div class="status-badge-online">🟢 System Status: Online (Groq Engine Active)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-badge-offline">🟡 System Status: Offline (Local Engine Active)</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 5. Session State Initializer
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Interactive Prompt Handling with Dynamic Tool Prompting
if prompt := st.chat_input("Ask a question, request a quiz, or summarize notes..."):
    
    # Tool-Specific Prompt Enhancements
    final_prompt = prompt
    if selected_tool == "📝 Quiz & MCQ Generator":
        final_prompt = f"Create a practice quiz with 5 Multiple Choice Questions (MCQs) and answers based on this topic: {prompt}"
    elif selected_tool == "📖 Lecture & Note Summarizer":
        final_prompt = f"Provide a structured summary with key bullet points and main concepts for the following content: {prompt}"
    elif selected_tool == "🧮 Math & Logic Problem Solver":
        final_prompt = f"Solve the following mathematical or logical problem step-by-step with clear explanations: {prompt}"

    # Append user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process response
    with st.chat_message("assistant"):
        response, mode_tag = router.get_response(final_prompt)
        full_response = f"{response}\n\n`{mode_tag}`"
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
