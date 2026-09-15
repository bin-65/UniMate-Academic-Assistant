import os
import requests
import streamlit as st

class LLMRouter:
    def __init__(self):
        try:
            # Streamlit secrets se key fetch karne ki koshish
            self.groq_api_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception as e:
            self.groq_api_key = ""
            st.error(f"Secrets Error Details: {e}")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"

    def is_online(self) -> bool:
        # Check karein ke key valid format ki hai aur khali nahi hai
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("gsk_yahan")

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. ONLINE MODE (Streamlit Cloud / Groq API)
        if self.is_online():
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are UniMate, an expert academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }
            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
                else:
                    # Agar Groq API ki taraf se koi error code aaye toh usay return karein
                    return f"**[Groq API Error]** Status Code: {response.status_code} - {response.text}", "[Error Mode]"
            except Exception as e:
                pass # Agar online request fail ho toh fallback ke tor par offline try karega

        # 2. OFFLINE MODE (Local PC / Ollama)
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 512,
                    "num_ctx": 2048,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=None)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return "**[Deployment Notice]** Aap app ko online (Streamlit Cloud) chala rahe hain, lekin Groq API key set nahi ki ya Ollama band hai. Baraye meharbani Streamlit Cloud ki settings mein ja kar `GROQ_API_KEY` add karein.", "[Error Mode]"
