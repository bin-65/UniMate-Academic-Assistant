import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        # Safe way to fetch Groq key from Streamlit Secrets or Environment Variables (No crashes!)
        self.groq_api_key = ""
        try:
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
            
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
        # 1. Try Groq (Online/Cloud) if key is available
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

        # 2. Fallback to Local Ollama (Offline Mode) if Groq isn't configured or fails
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

        # 3. Graceful fallback message if neither is available
        return "⚠️ **Connection Notice:** Na toh Groq API key mili hai aur na hi local Ollama chal raha hai. Baraye meharbani ya toh Ollama on karein ya secrets check karein.", "[Error Mode]"
