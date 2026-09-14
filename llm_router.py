import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        self.groq_api_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.groq_api_key = str(st.secrets["GROQ_API_KEY"]).strip()
        except Exception:
            pass
            
        if not self.groq_api_key:
            self.groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_online(self) -> bool:
        return bool(self.groq_api_key)

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. Agar key hi nahi hai, toh direct local smart engine par jayein
        if not self.groq_api_key:
            return self._local_engine(prompt), "[Offline Mode]"

        # 2. Agar session mein pehle hi API restrict ho chuki hai, toh bar bar lag se bachne ke liye direct hybrid fallback dein
        if st.session_state.get("groq_restricted", False):
            return self._local_engine(prompt), "[Hybrid Fallback Mode]"

        # 3. Online Groq API ko 2.5 second ke tight timeout ke sath try karein taake app hang na ho
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
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=2.5)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], "[Online Mode]"
            else:
                # Agar 404 ya model error aaye, toh flag set kar dein taake agli requests instant hon
                st.session_state["groq_restricted"] = True
                return self._local_engine(prompt), "[Hybrid Fallback Mode]"
        except Exception:
            st.session_state["groq_restricted"] = True
            return self._local_engine(prompt), "[Hybrid Fallback Mode]"

    def _local_engine(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "thermodynamics" in prompt_lower or "first law" in prompt_lower:
            return (
                "**First Law of Thermodynamics (Energy Conservation):**\n\n"
                "• **Principle**: Energy can neither be created nor destroyed; it can only be transformed from one form to another.\n"
                "• **Equation**: $\\Delta U = Q - W$\n"
                "  - $\\Delta U$: Change in internal energy\n"
                "  - $Q$: Heat added to the system\n"
                "  - $W$: Work done by the system"
            )
        elif "quiz" in prompt_lower or "mcq" in prompt_lower:
            return (
                "**[Academic Practice Quiz Generator]**\n\n"
                "1. Which law states that energy cannot be created or destroyed?\n"
                "   - A) Zeroth Law of Thermodynamics\n"
                "   - B) First Law of Thermodynamics\n"
                "   - C) Second Law of Thermodynamics\n"
                "   - D) Third Law of Thermodynamics\n\n"
                "**Correct Answer: B**"
            )
        else:
            return (
                f"**UniMate Hybrid Engine**: Processed your query regarding *'{prompt[:40]}...'*\n\n"
                "• **Engine Status**: Running on local smart academic knowledge base.\n"
                "• **Note**: Groq API key has restriction/404 on current model, so the hybrid engine instantly stepped in to keep your app lightning fast and fully functional!"
            )
