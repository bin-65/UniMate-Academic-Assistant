import os
import requests

class LLMRouter:
    def __init__(self):
        # Yahan apni asli Groq API key paste karein (agar online use karni hai)
        self.groq_api_key = "gsk_yahan_apni_asli_key_dal_do"
            
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://127.0.0.1:11434/api/generate"

    def is_online(self) -> bool:
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("gsk_yahan")

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. Try Groq Online API first if valid key exists
        if self.is_online():
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            models_to_try = [
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
                "gemma2-9b-it"
            ]
            
            for model_name in models_to_try:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You are UniMate, an expert academic assistant for university students."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }

                try:
                    response = requests.post(self.groq_url, headers=headers, json=payload, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
                except Exception:
                    pass

        # 2. Fallback to Local Ollama if Groq is not configured or fails
        try:
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=8.0)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
        except Exception:
            pass

        # 3. If both fail
        return "**[Connection Notice]** Running in local fallback mode. Please ensure Ollama is running locally (`ollama serve`) or provide a valid Groq API key in `llm_router.py`.", "[Local Mode]"
