import os
import streamlit as st
from connection_checker import is_connected

class LLMRouter:
    def __init__(self):
        # Safe lookup without throwing StreamlitSecretNotFoundError
        try:
            self.groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
        except Exception:
            self.groq_api_key = os.getenv("GROQ_API_KEY", "")

    def generate_response(self, prompt, context=""):
        if is_connected() and self.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return f"[Online Mode] {response.choices[0].message.content}"
            except Exception as e:
                return self._offline_fallback(prompt)
        else:
            return self._offline_fallback(prompt)

    def _offline_fallback(self, prompt):
        return f"[Offline Mode] Active: Processing query locally..."
