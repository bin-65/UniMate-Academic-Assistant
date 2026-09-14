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

# --- Custom Styling ---
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("### 🎓 UniMate Control Panel")
    st.markdown("Hybrid Smart Learning Engine for Academic Success.")
    st.markdown("---")
    
    # Engine Status Indicator
    is_online_status = router.is_online()
    if is_online_status:
        st.success("🟢 Engine Status: Hybrid Active (Online/Local)")
    else:
        st.warning("🟡 Engine Status: Local Smart Mode")
        
    st.markdown("### 🛠️ Quick Navigation")
    app_mode = st.radio(
        "Select Module:",
        ["💬 Assistant Chat", "📝 Quiz & MCQ Generator", "📖 PDF Lecture Summarizer", "🧮 Math & Logic Solver"]
    )
    
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.markdown("- **Thermodynamics & Laws**\n- **Engineering Calculations**\n- **PDF Notes Analysis**")

# --- Main App Title ---
st.markdown('<p class="main-header">🎓 UniMate Academic Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your lightning-fast hybrid study companion for university success</p>', unsafe_allow_html=True)

# ==========================================
# MODULE 1: ASSISTANT CHAT
# ==========================================
if app_mode == "💬 Assistant Chat":
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
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response using hybrid router
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text, mode_tag = router.get_response(prompt)
                st.markdown(response_text)
                st.caption(f"Engine Mode: {mode_tag}")
                
                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text, 
                    "mode": mode_tag
                })

# ==========================================
# MODULE 2: QUIZ & MCQ GENERATOR
# ==========================================
elif app_mode == "📝 Quiz & MCQ Generator":
    st.markdown("### 📝 Interactive Quiz & MCQ Generator")
    st.markdown("Test your knowledge instantly on any academic subject.")

    subject = st.text_input("Enter Subject or Topic (e.g., Thermodynamics, Data Structures, Cyber Law):", "Thermodynamics")
    
    if st.button("Generate Practice Quiz"):
        with st.spinner("Generating custom practice questions..."):
            quiz_prompt = f"Generate 3 multiple-choice questions (MCQs) with answers and brief explanations for university students on the topic: {subject}"
            response_text, mode_tag = router.get_response(quiz_prompt)
            
            st.markdown("---")
            st.markdown("### 📋 Generated Practice Quiz")
            st.markdown(response_text)
            st.caption(f"Engine Mode: {mode_tag}")

# ==========================================
# MODULE 3: PDF LECTURE SUMMARIZER
# ==========================================
elif app_mode == "📖 PDF Lecture Summarizer":
    st.markdown("### 📖 PDF Lecture Notes & Document Summarizer")
    st.markdown("Upload your semester notes, research papers, or study guides to extract key insights instantly.")

    uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])
    
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
                    
                if st.button("Extract Key Summary & Action Items"):
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
# MODULE 4: MATH & LOGIC SOLVER
# ==========================================
elif app_mode == "🧮 Math & Logic Solver":
    st.markdown("### 🧮 Math, Formula & Engineering Logic Solver")
    st.markdown("Step-by-step breakdown of equations, formulas, and technical problem statements.")

    math_query = st.text_area("Enter Math/Engineering Problem or Formula Question:", "Explain the formula for First Law of Thermodynamics and solve a sample problem.")
    
    if st.button("Solve Step-by-Step"):
        with st.spinner("Solving problem with step-by-step logic..."):
            solver_prompt = f"Provide a detailed step-by-step mathematical or logical solution for: {math_query}"
            response_text, mode_tag = router.get_response(solver_prompt)
            
            st.markdown("---")
            st.markdown("### 📐 Step-by-Step Solution")
            st.markdown(response_text)
            st.caption(f"Engine Mode: {mode_tag}")
