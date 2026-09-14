import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = st.secrets["GROQ_API_KEY"]
        except Exception as e:
            self.groq_api_key = f"Secret Error: {e}"
            
        if not self.groq_api_key or str(self.groq_api_key).startswith("Secret Error"):
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_online(self) -> bool:
        return True

    def get_response(self, prompt: str) -> tuple[str, str]:
        # Debug: Check key presence and length directly on screen
        if not self.groq_api_key or len(str(self.groq_api_key)) < 10:
            return f"**[CRITICAL DEBUG]** `GROQ_API_KEY` is missing or empty! Value found: `{repr(self.groq_api_key)}`. Check your Streamlit Cloud Secrets.", "[No Key]"

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are UniMate, an expert academic assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 512
        }

        try:
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], "[Online Mode]"
            else:
                return f"**Groq API Rejected Key (Status {response.status_code}):** {response.text}", "[API Rejected]"
        except Exception as e:
            return f"**Network Exception:** {str(e)}", "[Connection Error]"
