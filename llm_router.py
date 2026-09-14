import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = st.secrets["GROQ_API_KEY"]
            elif "groq" in st.secrets and "api_key" in st.secrets["groq"]:
                self.groq_api_key = st.secrets["groq"]["api_key"]
        except Exception:
            pass
            
        if not self.groq_api_key:
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.models_to_try = [
            "llama3-8b-8192",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile"
        ]

    def get_response(self, prompt: str) -> tuple[str, str]:
        if not self.groq_api_key:
            return "**[Error]** GROQ_API_KEY missing in Streamlit Secrets.", "[Missing Key]"

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
                    return data['choices'][0]['message']['content'], "[Online Mode]"
                else:
                    error_logs.append(f"{model_name}: Status {response.status_code} - {response.text}")
            except Exception as e:
                error_logs.append(f"{model_name}: Exception - {str(e)}")

        # If all fail, display the exact errors on screen so we know the root cause
        return f"**Groq Connection Failed on All Models:**\n\n" + "\n".join(f"- {err}" for err in error_logs), "[API Error]"
