import os
import requests
import streamlit as st
from groq import Groq

class LLMRouter:
    def __init__(self):
        self.groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

    def query(self, prompt: str, context: str, is_online: bool) -> tuple[str, str]:
        system_instruction = (
            "You are UniMate, an AI Academic Assistant. "
            "Answer strictly using the provided context. "
            "If the information is not in the context, explicitly state that you cannot find it in the trusted knowledge base."
        )
        
        full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

        # 1. ONLINE MODE (Groq API)
        if is_online and self.groq_api_key:
            models_to_try = ["llama-3.1-8b-instant", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]
            for model_name in models_to_try:
                try:
                    client = Groq(api_key=self.groq_api_key)
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.2,
                    )
                    return completion.choices[0].message.content, f"Groq Cloud AI ({model_name})"
                except Exception:
                    continue

        # 2. OFFLINE MODE (Local Ollama Fallback)
        try:
            # Check if local Ollama server is active on localhost
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"{system_instruction}\n\n{full_prompt}",
                    "stream": False
                },
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("response", ""), "Local Ollama AI (Offline)"
        except Exception:
            pass

        # 3. SAFE GRACEFUL FALLBACK (Error display standard format)
        if is_online:
            return "⚠️ **Groq API Error:** Please verify your API Key in Streamlit Secrets.", "API Configuration Error"
        else:
            return (
                "📶 **Offline Mode Active:** Internet connection unavailable and local Ollama instance was not detected on `http://localhost:11434`.\n\n"
                "**To run offline locally:**\n"
                "1. Download & Install [Ollama](https://ollama.com/download).\n"
                "2. Run `ollama run llama3` in terminal.",
                "Offline Engine Unavailable"
            )
