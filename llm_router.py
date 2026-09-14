import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
            
        if not self.groq_api_key:
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Comprehensive model list to auto-bypass any 404 model not found errors
        self.models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]

    def is_online(self) -> bool:
        return True

    def get_response(self, prompt: str) -> tuple[str, str]:
        if not self.groq_api_key:
            return "**[Error]** GROQ_API_KEY is missing in Streamlit Secrets.", "[No Key]"

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": "You are UniMate, an expert academic assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        error_logs = []
        for model_name in self.models_to_try:
            payload["model"] = model_name
            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'], f"[Online Mode]"
                else:
                    error_logs.append(f"{model_name}: {response.status_code}")
            except Exception as e:
                error_logs.append(f"{model_name}: Error")

        return f"**Groq API Error:** All fallback models tried. Details: {', '.join(error_logs)}", "[API Error]"
