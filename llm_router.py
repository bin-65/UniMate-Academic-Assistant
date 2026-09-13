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

        # 1. Direct Groq Cloud Execution
        if is_online and self.groq_api_key:
            try:
                client = Groq(api_key=self.groq_api_key)
                completion = client.chat.completions.create(
                    # Valid & updated Groq model name
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.2,
                )
                return completion.choices[0].message.content, "Groq Cloud AI (Online)"
            except Exception as e:
                # Secondary Fallback Model (llama-3.1-8b-instant) agar primary limit hit ho
                try:
                    client = Groq(api_key=self.groq_api_key)
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.2,
                    )
                    return completion.choices[0].message.content, "Groq Cloud AI (Fallback 8B)"
                except Exception as fallback_error:
                    return f"⚠️ Groq API Error: {str(fallback_error)}", "Groq API Error"

        # 2. Local Ollama Execution (Only when Offline)
        if not is_online:
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": f"{system_instruction}\n\n{full_prompt}",
                        "stream": False
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json().get("response", ""), "Local Ollama AI (Offline)"
            except Exception:
                return "⚠️ Local Offline Model Unavailable. Please start Ollama on your local machine.", "Offline Error"

        return "⚠️ API Key Missing. Please set GROQ_API_KEY in Streamlit Cloud Secrets.", "Configuration Error"
