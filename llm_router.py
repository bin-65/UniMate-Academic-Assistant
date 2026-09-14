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

    def is_online(self) -> bool:
        """Always return True if API key exists, bypassing external ping blocks"""
        return bool(self.groq_api_key)

    def get_response(self, prompt: str) -> tuple[str, str]:
        """Route query directly to Groq API using available models"""
        if not self.groq_api_key:
            return self._offline_fallback_response(prompt), "[Offline Mode]"

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

        # Try models sequentially until one succeeds
        for model_name in self.models_to_try:
            payload["model"] = model_name
            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=12)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'], "[Online Mode]"
            except Exception:
                continue

        # Fallback to local rules engine only if all models fail
        return self._offline_fallback_response(prompt), "[Offline Mode]"

    def _offline_fallback_response(self, prompt: str) -> str:
        """Rules-based academic offline engine when API fails"""
        prompt_lower = prompt.lower()
        
        if "quiz" in prompt_lower or "mcq" in prompt_lower:
            return (
                "**[Offline Practice Quiz - Sample Mode]**\n\n"
                "1. Which of the following best describes the principle of conservation of energy?\n"
                "   - A) Energy can be created out of nothing\n"
                "   - B) Energy cannot be created or destroyed, only transformed\n"
                "   - C) Total energy decreases over time\n"
                "   - **Answer: B**"
            )
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return (
                "**[Offline Summary Engine]**\n\n"
                "• **Key Concept**: Academic notes/lecture summary requested.\n"
                "• **Main Takeaway**: Core definitions and essential terms identified."
            )
        elif "math" in prompt_lower or "solve" in prompt_lower:
            return (
                "**[Offline Logic Engine]**\n\n"
                "For mathematical equations, apply standard step-by-step resolution:\n"
                "1. Identify knowns & unknowns.\n"
                "2. Apply relevant formula.\n"
                "3. Compute final values."
            )
        else:
            return (
                f"**UniMate Offline Mode**: Received your query regarding '{prompt[:50]}...'\n\n"
                "I am currently operating on the local offline fallback engine. "
                "For detailed AI answers, please ensure your Groq API key is valid."
            )
