import os
import requests
import streamlit as st
import google.generativeai as genai

class LLMRouter:
    def __init__(self):
        self.api_key = ""
        try:
            if "GEMINI_API_KEY" in st.secrets:
                self.api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
            
        if not self.api_key:
            self.api_key = os.environ.get("GEMINI_API_KEY", "") 

        self.gemini_enabled = False
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_enabled = True
            except:
                self.gemini_enabled = False
            
        self.gemini_model_name = "gemini-1.5-flash"
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        
        # Available local models
        self.ollama_models = ["qwen2.5:3b", "llama3:latest"]

    def is_online(self) -> bool:
        return self.gemini_enabled

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. Online Gemini (Agar internet aur key available ho)
        if self.gemini_enabled:
            try:
                model = genai.GenerativeModel(self.gemini_model_name)
                response = model.generate_content(prompt)
                if response and hasattr(response, 'text') and response.text:
                    return response.text, "[Online Mode (Google Gemini)]"
            except Exception:
                pass 

        # 2. Local Ollama (Timeout 300 seconds / 5 minutes set kar diya hai)
        for model_name in self.ollama_models:
            try:
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 1024,
                        "num_ctx": 4096,
                        "temperature": 0.7
                    }
                }
                
                # 300 seconds timeout taake heavy model ko poora waqt mil sake
                response = requests.post(self.ollama_url, json=payload, timeout=300.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data:
                        return data.get('response', ''), f"[Offline Mode (Ollama - {model_name})]"
            except Exception:
                continue

        return "⚠️ **Connection Error:** Local Ollama server did not respond within the 5-minute timeout.", "[Error Mode]"
