import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        # Safe tarike se secrets uthane ke liye try-except use karein
        try:
            self.groq_api_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            self.groq_api_key = ""
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"

    def is_online(self) -> bool:
        # Check karein ke key mojood hai aur khali nahi hai
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("gsk_yahan")
