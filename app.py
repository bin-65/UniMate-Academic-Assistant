import streamlit as st
from llm_router import LLMRouter

# Is decorator ki waja se router sirf aik dafa memory mein load hoga, baar baar nahi!
@st.cache_resource
def get_router():
    return LLMRouter()

# Phir app mein jahan bhi router use karna ho, aisay call karein:
router = get_router()

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
    .stApp {
        background-image: linear-gradient(rgba(248, 250, 252, 0.90), rgba(241, 245, 249, 0.94)), 
                          url('https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
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
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #0F172A !important;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
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

# --- Helper Function to Extract Text from Multiple Formats ---
def extract_document_text(uploaded_file) -> str:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    extracted_text = ""
    
    try:
        if file_extension == 'pdf':
            file_bytes = uploaded_file.read()
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                extracted_text += page.get_text() + "\n"
                
        elif file_extension == 'docx':
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"
                
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file, sheet_name=None)
            for sheet_name, sheet_df in df.items():
                extracted_text += f"\n--- Sheet: {sheet_name} ---\n"
                extracted_text += sheet_df.to_string(index=False) + "\n"
    except Exception as e:
        extracted_text = f"Error reading document: {str(e)}"
        
    return extracted_text

# --- Sidebar: Document Uploader & Controls ---
with st.sidebar:
    st.markdown("### 🎓 UniMate Control Panel")
    st.markdown("Hybrid Smart Learning Engine")
    st.markdown("---")
    
    # 📁 Document Uploader (Prominently placed at the top of the sidebar)
    st.markdown("### 📁 Document Knowledge Base")
    st.markdown("Upload **PDF, Word, or Excel** files:")
    
    uploaded_doc = st.file_uploader("Choose a study file", type=["pdf", "docx", "xlsx", "xls"], key="sidebar_file_uploader")
    
    if uploaded_doc is not None:
        with st.spinner("Processing document..."):
            document_context = extract_document_text(uploaded_doc)
            st.session_state["uploaded_doc_text"] = document_context
            st.success(f"✅ Loaded: {uploaded_doc.name}")
            with st.expander("Preview Extracted Data"):
                st.write(document_context[:600] + "..." if len(document_context) > 600 else document_context)
    elif "uploaded_doc_text" in st.session_state and st.session_state["uploaded_doc_text"]:
        st.info("📌 Active Document Loaded in Memory")

    st.markdown("---")
    
    # Engine Status Indicator
    if router.is_online():
        st.success("🟢 Engine Status: Hybrid Active")
    else:
        st.warning("🟡 Engine Status: Local Smart Mode")
        
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.markdown("- Upload your files above.\n- Ask questions in any tab!")

# --- Main App Title ---
st.markdown('<p class="main-header">🎓 UniMate Academic Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your lightning-fast hybrid study platform for university success</p>', unsafe_allow_html=True)

# --- Front-and-Center Feature Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Assistant Chat", 
    "📝 Quiz & MCQ Generator", 
    "📖 Document Summarizer", 
    "🧮 Math & Logic Solver"
])

# ==========================================
# TAB 1: ASSISTANT CHAT (Context-Aware)
# ==========================================
with tab1:
    st.markdown("### 💬 Academic Chat Assistant")
    st.markdown("Ask general questions or query your uploaded document/notes.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am UniMate. Upload any PDF, Word, or Excel file in the sidebar and ask me anything about it!", "mode": "[System]"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "mode" in message:
                st.caption(f"Engine Mode: {message['mode']}")

    if prompt := st.chat_input("Ask a question about your notes or general academics..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing with document context..."):
                active_context = st.session_state.get("uploaded_doc_text", "")
                if active_context:
                    full_prompt = f"Context from uploaded document:\n{active_context[:4000]}\n\nUser Question: {prompt}"
                else:
                    full_prompt = prompt

                response_text, mode_tag = router.get_response(full_prompt)
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
    st.markdown("Test your knowledge based on subjects or your uploaded document.")

    default_topic = "Uploaded Document Content" if "uploaded_doc_text" in st.session_state and st.session_state["uploaded_doc_text"] else "Thermodynamics"
    subject = st.text_input("Enter Topic or Subject:", default_topic, key="quiz_subject_input")
    
    if st.button("Generate Practice Quiz", key="generate_quiz_btn"):
        with st.spinner("Generating custom practice questions..."):
            active_context = st.session_state.get("uploaded_doc_text", "")
            if active_context:
                quiz_prompt = f"Based on the following document text, generate 3 multiple-choice questions (MCQs) with answers and explanations:\n\n{active_context[:3500]}"
            else:
                quiz_prompt = f"Generate 3 multiple-choice questions (MCQs) with answers and explanations for university students on the topic: {subject}"
                
            response_text, mode_tag = router.get_response(quiz_prompt)
            
            st.markdown("---")
            st.markdown("### 📋 Generated Practice Quiz")
            st.markdown(response_text)
            st.caption(f"Engine Mode: {mode_tag}")

# ==========================================
# TAB 3: DOCUMENT SUMMARIZER
# ==========================================
with tab3:
    st.markdown("### 📖 Document Notes & File Summarizer")
    st.markdown("Summarize your uploaded PDF, Word, or Excel document instantly.")

    if "uploaded_doc_text" in st.session_state and st.session_state["uploaded_doc_text"]:
        st.success("File is loaded from the sidebar! Click below to generate summary.")
        if st.button("Extract Key Summary & Revision Notes", key="summary_btn_main"):
            with st.spinner("Summarizing document content..."):
                doc_text = st.session_state["uploaded_doc_text"]
                summary_prompt = f"Summarize the following document into key bullet points, core concepts, and exam revision notes:\n\n{doc_text[:4000]}"
                response_text, mode_tag = router.get_response(summary_prompt)
                
                st.markdown("---")
                st.markdown("### 📝 Smart Summary & Takeaways")
                st.markdown(response_text)
                st.caption(f"Engine Mode: {mode_tag}")
    else:
        st.info("👈 Please upload a PDF, Word (.docx), or Excel (.xlsx) file in the sidebar first to use this summarizer.")

# ==========================================
# TAB 4: MATH & LOGIC SOLVER
# ==========================================
with tab4:
    st.markdown("### 🧮 Math, Formula & Engineering Logic Solver")
    st.markdown("Solve technical problems from your notes or general equations.")

    math_query = st.text_area("Enter Math/Engineering Problem:", "Explain the formula for First Law of Thermodynamics and solve a sample problem.", key="math_query_input")
    
    if st.button("Solve Step-by-Step", key="math_solve_btn"):
        with st.spinner("Solving problem with step-by-step logic..."):
            active_context = st.session_state.get("uploaded_doc_text", "")
            if active_context:
                solver_prompt = f"Using context from the uploaded document if relevant, provide a detailed step-by-step solution for: {math_query}\n\nDocument Context:\n{active_context[:2500]}"
            else:
                solver_prompt = f"Provide a detailed step-by-step mathematical or logical solution for: {math_query}"
                
            response_text, mode_tag = router.get_response(solver_prompt)
            
            st.markdown("---")
            st.markdown("### 📐 Step-by-Step Solution")
            st.markdown(response_text)
            st.caption(f"Engine Mode: {mode_tag}")
