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
        
        # Updated list containing current active Groq model IDs
        self.models_to_try = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-20b",
            "qwen/qwen3-32b"
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
                {"role": "system", "content": "You are UniMate, an expert academic assistant for university students."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        # Check cached model first for instant speed
        if "working_groq_model" in st.session_state:
            payload["model"] = st.session_state["working_groq_model"]
            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'], "[Online Mode]"
            except Exception:
                pass

        detailed_errors = []
        for model_name in self.models_to_try:
            payload["model"] = model_name
            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["working_groq_model"] = model_name
                    return data['choices'][0]['message']['content'], "[Online Mode]"
                else:
                    err_msg = response.json().get("error", {}).get("message", response.text)
                    detailed_errors.append(f"Model `{model_name}` ({response.status_code}): {err_msg}")
            except Exception as e:
                detailed_errors.append(f"Model `{model_name}` Exception: {str(e)}")

        return f"**Groq API Connection Failed:**\n\n" + "\n".join(detailed_errors), "[API Error]"
