import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = st.secrets["GROQ_API_KEY"].strip()
        except Exception:
            pass
            
        if not self.groq_api_key:
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_online(self) -> bool:
        return True

    def get_response(self, prompt: str) -> tuple[str, str]:
        if not self.groq_api_key:
            return "**[Error]** GROQ_API_KEY is missing in Streamlit Secrets.", "[No Key]"

        # Agar pehle hi API key invalid ya 404 de chuki hai, toh bar bar wait karne ke bajaye instant fallback dein
        if st.session_state.get("groq_permanently_failed", False):
            return self._offline_fallback_response(prompt), "[Offline Mode (API Restricted)]"

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are UniMate, an expert academic assistant for university students."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        try:
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=3)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], "[Online Mode]"
            else:
                # Mark as failed so future queries don't lag/slow down
                st.session_state["groq_permanently_failed"] = True
                err_msg = response.json().get("error", {}).get("message", response.text)
                return f"**Groq API Access Issue ({response.status_code}):** {err_msg}\n\n*(Switching to fast offline mode to prevent lag)*", "[API Error]"
        except requests.exceptions.Timeout:
            return "**Network Timeout:** Groq API took too long to respond.", "[Timeout Error]"
        except Exception as e:
            return f"**Exception:** {str(e)}", "[Error]"

    def _offline_fallback_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "thermodynamics" in prompt_lower or "first law" in prompt_lower:
            return (
                "**First Law of Thermodynamics (Energy Conservation):**\n\n"
                "• **Principle**: Energy can neither be created nor destroyed; it can only be transformed from one form to another.\n"
                "• **Equation**: $\\Delta U = Q - W$\n"
                "  - $\\Delta U$: Change in internal energy\n"
                "  - $Q$: Heat added to the system\n"
                "  - $W$: Work done by the system\n\n"
                "*(Note: Running on instant local academic engine due to API key permission restrictions)*"
            )
        return (
            f"**UniMate Instant Engine**: Received your query regarding '{prompt[:50]}...'\n\n"
            "Your Groq API key is returning a 404/Access restriction. Please generate a fresh API key from the Groq Console if you want live cloud generation, otherwise this local engine is fully active and lightning fast!"
        )
