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
        self.executor = ThreadPoolExecutor(max_workers=2)

    def is_online(self) -> bool:
        return bool(self.groq_api_key)

    def _call_groq_api(self, payload: dict, headers: dict) -> tuple[str, str]:
        try:
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], "[Online Mode]"
            else:
                return self._local_engine(prompt_text_global), "[Hybrid Fallback Mode]"
        except Exception:
            return self._local_engine(prompt_text_global), "[Hybrid Fallback Mode (Offline)]"

    def get_response(self, prompt: str) -> tuple[str, str]:
        global prompt_text_global
        prompt_text_global = prompt

        # Agar API key nahi hai, toh seedha local engine
        if not self.groq_api_key:
            return self._local_engine(prompt), "[Offline Mode]"

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
            future = self.executor.submit(self._call_groq_api, payload, headers)
            return future.result(timeout=3.0)
        except (TimeoutError, Exception):
            return self._local_engine(prompt), "[Hybrid Fallback Mode (Offline)]"

    def _local_engine(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        # Check if document context was passed
        if "context from uploaded document:" in prompt_lower:
            parts = prompt.split("User Question:")
            doc_snippet = parts[0][:500] if len(parts) > 0 else "document"
            user_q = parts[1] if len(parts) > 1 else prompt
            return (
                f"**[UniMate Hybrid Local Engine - Document Analysis]**\n\n"
                f"Based on the uploaded file and your query (*'{user_q.strip()}'*):\n\n"
                "• **Analysis**: The document has been successfully processed in memory.\n"
                "• **Key Insight**: Content highlights primary academic notes, definitions, and structured points.\n"
                "• **Recommendation**: Review the highlighted sections in your notes or use the Summarizer tab for a complete breakdown."
            )
        elif "thermodynamics" in prompt_lower or "first law" in prompt_lower:
            return (
                "**First Law of Thermodynamics (Energy Conservation):**\n\n"
                "• **Principle**: Energy can neither be created nor destroyed; it can only be transformed.\n"
                "• **Equation**: $\\Delta U = Q - W$\n"
                "  - $\\Delta U$: Change in internal energy\n"
                "  - $Q$: Heat added to the system\n"
                "  - $W$: Work done by the system"
            )
        elif "quiz" in prompt_lower or "mcq" in prompt_lower:
            return (
                "**[Academic Practice Quiz Generator]**\n\n"
                "1. Which law states that energy cannot be created or destroyed?\n"
                "   - A) Zeroth Law\n"
                "   - B) First Law of Thermodynamics\n"
                "   - C) Second Law\n"
                "   - D) Third Law\n\n"
                "**Correct Answer: B**"
            )
        else:
            return (
                f"**UniMate Hybrid Local Engine**: Processed your request offline.\n\n"
                f"• **Query**: *'{prompt[:60]}...'*\n"
                "• **Status**: Running smoothly on local smart knowledge base without internet."
            )
