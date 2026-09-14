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
        self.model_name = "llama-3.1-8b-instant"

    def get_response(self, prompt: str) -> tuple[str, str]:
        # Check if key is loaded at all
        if not self.groq_api_key:
            return f"**Debug Error:** `GROQ_API_KEY` not found in Streamlit Secrets or Environment Variables!", "[Config Error]"

        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are UniMate, an expert academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], "[Online Mode]"
            else:
                # Show the exact Groq API error response on screen
                return f"**Groq API Error ({response.status_code}):** {response.text}", "[API Error]"
                
        except Exception as e:
            return f"**Connection Exception:** {str(e)}", "[Network Error]"
