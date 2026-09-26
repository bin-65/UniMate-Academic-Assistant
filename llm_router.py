import os
import requests
import streamlit as st
import google.generativeai as genai

class LLMRouter:
    def __init__(self):
        # Google AI Studio API Key setup
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
        
        # Local Ollama setup (Aapke paas mojood models ki list)
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model_names = ["qwen2.5:3b", "llama3:latest"]

    def is_online(self) -> bool:
        return self.gemini_enabled

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. Pehle Online Gemini API try karega agar key maujood hai aur net chal raha hai
        if self.api_key:
            try:
                model = genai.GenerativeModel(self.gemini_model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text, "[Online Mode (Google Gemini)]"
            except Exception as e:
                pass

        # 2. Offline Fallback: Local Ollama (Checking both available models)
        for model_name in self.ollama_model_names:
            try:
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 512,
                        "num_ctx": 2048,
                        "temperature": 0.7
                    }
                }
                
                response = requests.post(self.ollama_url, json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data:
                        return data.get('response', ''), f"[Offline Mode (Ollama - {model_name})]"
            except Exception as e:
                continue

        # Agar sab fail ho jayein
        return "⚠️ **Connection Error:** Neither Online Gemini API nor Local Ollama is responding. Please check your internet or start Ollama.", "[Error Mode]"
