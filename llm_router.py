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
            
        print(f"DEBUG: Loaded API Key length -> {len(self.groq_api_key)}")
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://127.0.0.1:11434/api/generate"

    def is_online(self) -> bool:
        return bool(self.groq_api_key)

    def get_response(self, prompt: str) -> tuple[str, str]:
        if self.groq_api_key:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are UniMate, an expert academic assistant for university students."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }

            try:
                response = requests.post(self.groq_url, headers=headers, json=payload, timeout=15.0)
                print(f"DEBUG: Groq Response Status Code -> {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
                else:
                    print(f"DEBUG: Groq Error Body -> {response.text}")
            except Exception as e:
                print(f"DEBUG: Groq Connection Exception -> {str(e)}")

        # Fallback to Ollama
        try:
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
        except Exception as e:
            pass

        return "**[Connection Error]** Both Groq and Ollama failed. Check terminal for details.", "[Error Mode]"
