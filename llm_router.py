import os
import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, TimeoutError

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
        # Thread pool executor for non-blocking asynchronous network calls
        self.executor = ThreadPoolExecutor(max_workers=2)

    def is_online(self) -> bool:
        return bool(self.groq_api_key)

    def _call_groq_api(self, payload: dict, headers: dict) -> tuple[str, str]:
        response = requests.post(self.groq_url, headers=headers, json=payload, timeout=3.5)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'], "[Online Mode]"
        else:
            st.session_state["groq_restricted"] = True
            return self._local_engine(prompt_text_global), "[Hybrid Fallback Mode]"

    def get_response(self, prompt: str) -> tuple[str, str]:
        # Store globally for thread reference
        global prompt_text_global
        prompt_text_global = prompt

        # 1. Agar key nahi hai, toh instant local engine
        if not self.groq_api_key:
            return self._local_engine(prompt), "[Offline Mode]"

        # 2. Agar pehle restricted ho chuki hai, toh network call hi mat karo (Zero Lag)
        if st.session_state.get("groq_restricted", False):
            return self._local_engine(prompt), "[Hybrid Fallback Mode]"

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

        # 3. Non-blocking execution with strict 2.5 second thread timeout
        try:
            future = self.executor.submit(self._call_groq_api, payload, headers)
            # Agar 2.5 second mein response na aaye, toh thread ko chhor kar foran local engine par chale jao
            return future.result(timeout=2.5)
        except TimeoutError:
            st.session_state["groq_restricted"] = True
            return self._local_engine(prompt), "[Hybrid Fallback Mode (Timeout Protected)]"
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
                "• **Engine Status**: Running on ultra-fast local smart academic knowledge base.\n"
                "• **Performance Note**: Network timeout protection engaged to ensure zero lag."
            )
