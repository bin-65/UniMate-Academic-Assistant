import os
import requests
import streamlit as st
import google.generativeai as genai

class LLMRouter:
    def __init__(self):
        # Google AI Studio API Key setup (Streamlit Secrets + Environment Variables support)
        self.api_key = ""
        try:
            if "GEMINI_API_KEY" in st.secrets:
                self.api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
            
        if not self.api_key:
            self.api_key = os.environ.get("GEMINI_API_KEY", "") 

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_enabled = True
            except:
                self.gemini_enabled = False
        else:
            self.gemini_enabled = False
            
        self.gemini_model_name = "gemini-1.5-flash"
        
        # Local Ollama fallback setup
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.ollama_model_name = "llama3:latest"
