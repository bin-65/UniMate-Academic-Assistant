import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        
        # 1. Pehle Session State check karo (agar user ne sidebar mein dali ho)
        if "user_groq_key" in st.session_state and st.session_state["user_groq_key"]:
            self.groq_api_key = st.session_state["user_groq_key"]
            
        # 2. Agar wahan nahi hai, toh Streamlit Secrets check karo
        if not self.groq_api_key:
            try:
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    self.groq_api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass
                
        # 3. Akhir mein Environment variable check karo
        if not self.groq_api_key:
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"
        
        self.fallback_models = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "llama3-8b-8192"
        ]

    def is_online(self) -> bool:
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("gsk_yahan")

    def get_response(self, prompt: str) -> tuple[str, str]:
        if self.is_online():
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            for model_id in self.fallback_models:
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "You are UniMate, an expert academic assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
                try:
                    response = requests.post(self.groq_url, headers=headers, json=payload, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        return data['choices'][0]['message']['content'], f"[Online Mode (Groq: {model_id})]"
                except Exception:
                    continue

        return "⚠️ **API Key Required:** Baraye meharbani sidebar mein apni Groq API Key enter karein taake app online chal sakay.", "[Error Mode]"
