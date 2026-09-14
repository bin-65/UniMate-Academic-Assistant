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
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.executor = ThreadPoolExecutor(max_workers=2)

    def is_online(self) -> bool:
        return bool(self.groq_api_key)

    def _call_groq_api(self, payload: dict, headers: dict) -> tuple[str, str]:
        try:
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=15.0)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
            else:
                return f"**[Groq API Error]** Status code {response.status_code}: {response.text}", "[Error Mode]"
        except Exception as e:
            return f"**[Connection Error]** Could not reach Groq API: {str(e)}", "[Error Mode]"

    def get_response(self, prompt: str) -> tuple[str, str]:
        if not self.groq_api_key:
            return self._local_engine(prompt), "[Offline Mode (Ollama - Qwen)]"

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",  # Groq's active current production model
            "messages": [
                {"role": "system", "content": "You are UniMate, an expert academic assistant for university students."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        try:
            future = self.executor.submit(self._call_groq_api, payload, headers)
            return future.result(timeout=16.0)
        except (TimeoutError, Exception) as e:
            return f"**[Router Timeout Error]** {str(e)}", "[Error Mode]"

    def _local_engine(self, prompt: str) -> str:
        try:
            payload = {
                "model": "qwen2.5:3b",
                "prompt": f"You are UniMate, an expert academic assistant for university students. Answer the following query clearly:\n\n{prompt}",
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=10.0)
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
