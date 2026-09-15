import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        try:
            self.groq_api_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception as e:
            self.groq_api_key = ""
            st.error(f"Secrets Error Details: {e}")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"
        
        # Fast & Active Models list (Sab se fast model sab se oopar rakha hai)
        self.fallback_models = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "llama3-8b-8192"
        ]

    def is_online(self) -> bool:
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("gsk_yahan")

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. ONLINE MODE (Groq API - Ultra Fast)
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
                    # Timeout ko 10 seconds kar diya hai taake app fast response de
                    response = requests.post(self.groq_url, headers=headers, json=payload, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        return data['choices'][0]['message']['content'], f"[Online Mode (Groq: {model_id})]"
                    else:
                        continue # Agar error ho toh foran aglay model par jao
                except Exception:
                    continue 

        # 2. OFFLINE MODE (Local PC / Ollama)
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
            else:
                return f"**[Ollama Error]** Status: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return "**[Connection Notice]** API key ya local server ka masla hai. Baraye meharbani connection check karein.", "[Error Mode]"
