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
        self.ollama_url = "http://localhost:11434/api/generate"
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

        # Agar API key nahi hai, toh seedha local Ollama engine
        if not self.groq_api_key:
            return self._local_engine(prompt), "[Offline Mode (Ollama)]"

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
            return self._local_engine(prompt), "[Hybrid Fallback Mode (Offline Ollama)]"

    def _local_engine(self, prompt: str) -> str:
        try:
            # Ollama local call (llama3:latest)
            payload = {
                "model": "llama3:latest",
                "prompt": f"You are UniMate, an expert academic assistant for university students. Answer the following query clearly:\n\n{prompt}",
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=15.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response generated from Ollama.")
            else:
                return f"**[Local Engine Error]** Ollama responded with status code {response.status_code}"
        except Exception as e:
            return (
                f"**[UniMate Offline Mode]**\n\n"
                f"Could not reach local Ollama server. Make sure `ollama serve` is running.\n"
                f"• **Error Details**: {str(e)}"
            )
