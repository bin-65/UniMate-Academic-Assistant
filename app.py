import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
from llm_router import LLMRouter

# --- Page Configuration ---
st.set_page_config(
    page_title="UniMate Academic Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Router ---
@st.cache_resource
def get_router():
    return LLMRouter()

router = get_router()

# --- Light Professional Library & Study Platform Styling ---
st.markdown("""
    <style>
    /* Main App Background with Light University Library Theme */
    .stApp {
        background-image: linear-gradient(rgba(248, 250, 252, 0.90), rgba(241, 245, 249, 0.94)), 
                          url('https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Custom Header Styling */
    .main-header {
        font-size: 2.4rem;
        color: #1E3A8A !important;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #475569 !important;
        margin-bottom: 25px;
    }

    /* Light Glassmorphism Container for Content */
    div.block-container {
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        color: #1E293B;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(241, 245, 249, 0.95);
        border-right: 1px solid rgba(203, 213, 225, 0.6);
    }
    section[data-testid="stSidebar"] .block-container {
        background: transparent;
        backdrop-filter: none;
        border: none;
        box-shadow: none;
    }

    /* Typography & Inputs for Light Theme */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #0F172A !important;
    }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    /* Buttons Styling */
    .stButton button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #1D4ED8 100%, #1E40AF 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Info ---
with st.sidebar:
    st.markdown("### 🎓 UniMate Control Panel")
    st.markdown("Hybrid Smart Learning Engine for Academic Success.")
    st.markdown("---")
    
    # Engine Status Indicator
    is_online_status = router.is_online()
    if is_online_status:
        st.success("🟢 Engine Status: Hybrid Active")
    else:
        st.warning("🟡 Engine Status: Local Smart Mode")
        
    st.markdown("---")
    st.markdown("### 💡 Study Quick Tips")
    st.markdown("- **Chat**: Ask conceptual questions\n- **Quiz**: Test your knowledge\n- **PDF**: Summarize notes instantly\n- **Math**: Step-by-step problem solver")

# --- Main App Title ---
st.markdown('<p class="main-header">🎓 UniMate Academic Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your lightning-fast hybrid study platform for university success</p>', unsafe_allow_html=True)

# --- Front-and-Center Feature Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Assistant Chat", 
    "📝 Quiz & MCQ Generator", 
    "📖 PDF Lecture Summarizer", 
    "🧮 Math & Logic Solver"
])

# ==========================================
# TAB 1: ASSISTANT CHAT
# ==========================================
with tab1:
    st.markdown("### 💬 Academic Chat Assistant")
    st.markdown("Ask general academic queries, essay guidance, conceptual clarifications, or research notes.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am UniMate. How can I help you with your studies today?", "mode": "[System]"}
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "mode" in message:
                st.caption(f"Engine Mode: {message['mode']}")

    # Chat Input
    if prompt := st.chat_input("Ask any academic question (e.g., Explain First Law of Thermodynamics)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text, mode_tag = router.get_response(prompt)
                st.markdown(response_text)
                st.caption(f"Engine Mode: {mode_tag}")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text, 
                    "mode": mode_tag
                })

# ==========================================
# TAB 2: QUIZ & MCQ GENERATOR
# ==========================================
with tab2:
    st.markdown("### 📝 Interactive Quiz & MCQ Generator")
    st.markdown("Test your knowledge instantly on any academic subject.")

    subject = st.text_input("Enter Subject or Topic (e.g., Thermodynamics, Data Structures, Cyber Law):", "Thermodynamics", key="quiz_subject_input")
    
    if st.button("Generate Practice Quiz"):
        with st.spinner("Generating custom practice questions..."):
            quiz_prompt = f"Generate 3 multiple-choice questions (MCQs) with answers and brief explanations for university students on the topic: {subject}"
            response_text, mode_tag = router.get_response(quiz_prompt)
            
            st.markdown("---")
            st.markdown("### 📋 Generated Practice Quiz")
            st.markdown(response_text)
            st.caption(f"Engine Mode: {mode_tag}")

# ==========================================
# TAB 3: PDF LECTURE SUMMARIZER
# ==========================================
with tab3:
    st.markdown("### 📖 PDF Lecture Notes & Document Summarizer")
    st.markdown("Upload your semester notes, research papers, or study guides to extract key insights instantly.")

    uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"], key="pdf_uploader_main")
    
    if uploaded_file is not None:
        with st.spinner("Reading document pages..."):
            try:
                file_bytes = uploaded_file.read()
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                
                text_content = ""
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content += page.get_text()
                
                total_words = len(text_content.split())
                
                st.success(f"Document Processed Successfully! | Pages: {len(doc)} | Total Words: {total_words}")
                
                with st.expander("🔍 View Raw Text Preview"):
                    st.write(text_content[:1500] + "..." if len(text_content) > 1500 else text_content)
                    
                if st.button("Extract Key Summary & Action Items", key="pdf_summary_btn"):
                    with st.spinner("Synthesizing core academic takeaways..."):
                        summary_prompt = f"Summarize the following academic notes into key bullet points and exam revision notes:\n\n{text_content[:4000]}"
                        response_text, mode_tag = router.get_response(summary_prompt)
                        
                        st.markdown("---")
                        st.markdown("### 📝 Smart Summary & Key Takeaways")
                        st.markdown(response_text)
                        st.caption(f"Engine Mode: {mode_tag}")
                        
            except Exception as e:
                st.error(f"Error reading PDF file: {str(e)}")

# ==========================================
# TAB 4: MATH & LOGIC SOLVER
# ==========================================
with tab4:
    st.markdown("### 🧮 Math, Formula & Engineering Logic Solver")
    st.markdown("Step-by-step breakdown of equations, formulas, and technical problem statements.")

    math_query = st.text_area("Enter Math/Engineering Problem or Formula Question:", "Explain the formula for First Law of Thermodynamics and solve a sample problem.", key="math_query_input")
    
    if st.button("Solve Step-by-Step", key="math_solve_btn"):
        with st.spinner("Solving problem with step-by-step logic..."):
            solver_prompt = f"Provide a detailed step-by-step mathematical or logical solution for: {math_query}"
            response_text, mode_tag = router.get_response(solver_prompt)
            
            st.markdown("---")
            st.markdown("### 📐 Step-by-Step Solution")
            st.markdown(response_text)
            st.caption(f"Engine Mode: {mode_tag}")
