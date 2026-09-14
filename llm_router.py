import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        
        # Check multiple possible formats in Streamlit secrets
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = st.secrets["GROQ_API_KEY"]
            elif "groq" in st.secrets and "api_key" in st.secrets["groq"]:
                self.groq_api_key = st.secrets["groq"]["api_key"]
            elif "GROQ" in st.secrets and "API_KEY" in st.secrets["GROQ"]:
                self.groq_api_key = st.secrets["GROQ"]["API_KEY"]
        except Exception:
            pass
            
        if not self.groq_api_key:
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # List of models to try automatically so it never fails on model-not-found
        self.models_to_try = [
            "llama3-8b-8192",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile"
        ]

    def is_online(self) -> bool:
        """Check internet & API key presence"""
        if not self.groq_api_key:
            return False
        try:
            requests.get("https://api.groq.com", timeout=3)
            return True
        except Exception:
            return False

    def get_response(self, prompt: str) -> tuple[str, str]:
        """Route query to Groq API or Local Fallback Engine"""
        if not self.groq_api_key:
            return (
                "**[Configuration Notice]** `GROQ_API_KEY` was not found in Streamlit Secrets.\n\n"
                "Please add your key in **Streamlit Cloud Dashboard -> Settings -> Secrets**.",
                "[Missing Key]"
            )

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

        # Try models sequentially until one works
        last_error = ""
        for model_name in self.models_to_try:
            payload["model"] = model_name
            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'], "[Online Mode]"
                else:
                    last_error = f"Model {model_name} error ({response.status_code}): {response.text}"
            except Exception as e:
                last_error = str(e)

        # If all online models fail, fallback gracefully
        return self._offline_fallback_response(prompt), "[Offline Mode]"

    def _offline_fallback_response(self, prompt: str) -> str:
        """Rules-based academic offline engine when internet/API is down"""
        prompt_lower = prompt.lower()
        
        if "quiz" in prompt_lower or "mcq" in prompt_lower:
            return (
                "**[Offline Practice Quiz - Sample Mode]**\n\n"
                "1. Which of the following best describes the principle of conservation of energy?\n"
                "   - A) Energy can be created out of nothing\n"
                "   - B) Energy cannot be created or destroyed, only transformed\n"
                "   - C) Total energy decreases over time\n"
                "   - **Answer: B**\n\n"
                "*(Connect to internet for dynamic AI-generated quizzes)*"
            )
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return (
                "**[Offline Summary Engine]**\n\n"
                "• **Key Concept**: Academic notes/lecture summary requested.\n"
                "• **Main Takeaway**: Core definitions and essential terms identified.\n"
                "• **Note**: Full natural language summarization requires online API connectivity."
            )
        elif "math" in prompt_lower or "solve" in prompt_lower:
            return (
                "**[Offline Logic Engine]**\n\n"
                "For mathematical equations, apply standard step-by-step resolution:\n"
                "1. Identify knowns & unknowns.\n"
                "2. Apply relevant algebraic formula.\n"
                "3. Compute final values.\n\n"
                "*(Connect online for full step-by-step AI derivations)*"
            )
        else:
            return (
                f"**UniMate Offline Mode**: Received your query regarding '{prompt[:50]}...'\n\n"
                "I am currently operating on the local offline fallback engine. "
                "For detailed AI answers, please ensure your Groq API key is valid and internet connectivity is restored."
            )
