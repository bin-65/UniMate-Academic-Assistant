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
        
        # Updated models list including lightweight & preview models
        self.models_to_try = [
            "llama-3.1-8b-instant",
            "llama-3.2-3b-preview",
            "llama-3.2-1b-preview",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768"
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

        detailed_errors = []
        for model_name in self.models_to_try:
            payload["model"] = model_name
            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'], "[Online Mode]"
                else:
                    # Capture the exact error message from Groq JSON response
                    err_msg = response.json().get("error", {}).get("message", response.text)
                    detailed_errors.append(f"Model `{model_name}` ({response.status_code}): {err_msg}")
            except Exception as e:
                detailed_errors.append(f"Model `{model_name}` Exception: {str(e)}")

        # If everything fails, show the exact detailed errors on screen
        error_report = "\n\n".join(detailed_errors)
        return f"**Detailed Groq Diagnostics:**\n\n{error_report}", "[API Error]"
