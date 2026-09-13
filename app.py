import os
import tempfile
import streamlit as st
from connection_checker import check_internet_connection
from rag_engine import RAGEngine
from llm_router import LLMRouter

st.set_page_config(page_title="UniMate - Academic Assistant", page_icon="🎓", layout="wide")

# Custom CSS for Professional Styling
st.markdown("""
<style>
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Custom Header Banner */
    .header-container {
        padding: 2rem 1rem;
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }

    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Styled Action Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5, #06b6d4);
        color: white !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Text Area Focus Ring */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom Header HTML Rendering
st.markdown("""
<div class="header-container">
    <div class="main-title">🎓 UniMate</div>
    <div class="subtitle">Hybrid Offline-Online RAG-Based AI Academic Assistant</div>
</div>
""", unsafe_allow_html=True)
