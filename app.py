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

# 2. Pure CSS Academic Library Theme (External URL Dependency Block Removed)
st.markdown("""
    <style>
    /* Full Page Academic Gradient + High Contrast Bookshelf Pattern */
    .stApp {
        background-color: #f1f5f9 !important;
        background-image: 
            linear-gradient(135deg, rgba(241, 245, 249, 0.85) 0%, rgba(226, 232, 240, 0.90) 100%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 200 200'%3E%3Cg fill='%231e293b' fill-opacity='0.15'%3E%3Cpath d='M15 40h20v140H15zM40 60h18v120H40zM62 30h24v150H62zM90 70h16v110H90zM110 50h20v130H110zM134 35h22v145H134zM160 55h18v125H160zM182 45h15v135H182z'/%3E%3Cpath d='M0 180h200v8H0z'/%3E%3Ccircle cx='50' cy='25' r='8'/%3E%3Cpath d='M120 15l15 20h-30z'/%3E%3C/g%3E%3C/svg%3E") !important;
        background-repeat: repeat !important;
        background-attachment: fixed !important;
        background-size: 180px 180px !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }

    /* Soft Glass Card Panels */
    div.stCard, div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.94) !important;
    }

    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.1rem;
    }

    .sub-title {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
        font-weight: 600;
    }

    .status-badge-online {
        padding: 8px 16px;
        background-color: #dcfce7;
        border: 1px solid #86efac;
        color: #15803d;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-offline {
        padding: 8px 16px;
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

# 3. Sidebar Storage Hub
with st.sidebar:
    st.title("⚙️ UniMate Storage")
    st.markdown("---")
    
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

# 4. Main Title & Connection Status
st.markdown('<h1 class="main-title">🎓 UniMate Academic Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Hybrid Smart Learning Engine for Academic Success</p>', unsafe_allow_html=True)

if router.is_online():
    st.markdown('<div class="status-badge-online">🟢 System Status: Online (Groq Engine Active)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-badge-offline">🟡 System Status: Offline (Local Engine Active)</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. Front-End Academic Tools (Tabs Layout)
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Assistant Chat", 
    "📝 Quiz & MCQ Generator", 
    "📖 Lecture Summarizer", 
    "🧮 Math & Logic Solver"
])

def handle_chat_input(prompt_text, prefix=""):
    if prompt_text:
        final_prompt = f"{prefix} {prompt_text}".strip()
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        
        with st.spinner("Processing request..."):
            response, mode_tag = router.get_response(final_prompt)
            full_response = f"{response}\n\n`{mode_tag}`"
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tab 1: Chat
with tab1:
    st.caption("Ask general academic queries, essay guidance, or concept clarifications.")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if p1 := st.chat_input("Ask UniMate anything...", key="chat_tab1"):
        handle_chat_input(p1)
        st.rerun()

# Tab 2: Quiz
with tab2:
    st.subheader("📝 Generate Practice Quizzes & MCQs")
    topic = st.text_input("Enter Topic or Subject Name:")
    if st.button("Generate Quiz Now", type="primary"):
        if topic:
            handle_chat_input(topic, prefix="Create a practice quiz with 5 Multiple Choice Questions (MCQs) and detailed answer key for:")
            st.rerun()

# Tab 3: Summarizer
with tab3:
    st.subheader("📖 Lecture & Note Summarizer")
    notes = st.text_area("Paste lecture text or topic overview here:")
    if st.button("Summarize Content", type="primary"):
        if notes:
            handle_chat_input(notes, prefix="Provide a structured academic summary with key takeaways and bullet points for:")
            st.rerun()

# Tab 4: Math Solver
with tab4:
    st.subheader("🧮 Step-by-Step Math & Logic Solver")
    problem = st.text_area("Enter equation or numerical problem:")
    if st.button("Solve Problem", type="primary"):
        if problem:
            handle_chat_input(problem, prefix="Solve the following mathematical or logical problem step-by-step with clear formulas and explanations:")
            st.rerun()
