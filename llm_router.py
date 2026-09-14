import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = str(st.secrets["GROQ_API_KEY"]).strip()
                print("DEBUG: Key successfully loaded from st.secrets!")
        except Exception as e:
            print(f"DEBUG: Error reading secrets: {e}")
            
        if not self.groq_api_key:
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
            print("DEBUG: Checking environment variables...")
            
        print(f"DEBUG: Final Loaded Key Status -> Present: {bool(self.groq_api_key)}")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://127.0.0.1:11434/api/generate"

    def is_online(self) -> bool:
        return bool(self.groq_api_key)

    def get_response(self, prompt: str) -> tuple[str, str]:
        if not self.groq_api_key:
            return "**[Configuration Error]** `GROQ_API_KEY` is missing in Streamlit secrets.", "[Error Mode]"

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are UniMate, an expert academic assistant for university students."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        try:
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=15.0)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
            else:
                return f"**[Groq API Error]** Status code {response.status_code}: {response.text}", "[Error Mode]"
        except Exception as e:
            return f"**[Connection Error]** Could not reach Groq API: {str(e)}", "[Error Mode]"
