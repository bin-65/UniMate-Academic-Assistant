import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"
        
        self.fallback_models = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "llama3-8b-8192"
        ]

    def get_current_key(self) -> str:
        # Har request ke waqt fresh key check karega (Session -> Secrets -> Env)
        if "user_groq_key" in st.session_state and st.session_state["user_groq_key"]:
            return st.session_state["user_groq_key"]
            
        try:
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                return st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
            
        return os.environ.get("GROQ_API_KEY", "")

    def is_online(self) -> bool:
        key = self.get_current_key()
        return bool(key) and not key.startswith("gsk_yahan")

    def get_response(self, prompt: str) -> tuple[str, str]:
        current_key = self.get_current_key()
        
        # 1. Try Groq (Online) if key exists
        if current_key and not current_key.startswith("gsk_yahan"):
            headers = {
                "Authorization": f"Bearer {current_key}",
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

        # 2. Fallback to Local Ollama
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 512,
                    "num_ctx": 2048,
                    "temperature": 0.7
                }
            }
            response = requests.post(self.ollama_url, json=payload, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
        except Exception:
            pass

        return "⚠️ **API Key Error:** Baraye meharbani sidebar mein apni valid Groq API Key enter karein.", "[Error Mode]"
