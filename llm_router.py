import os
import requests

class LLMRouter:
    def __init__(self):
        # Yahan apni real Groq API key dal dein (agar online chalana hai)
        # Agar key nahi dali gi ya placeholder rahe ga, toh app automatically offline Ollama par chalegi
        self.groq_api_key = "gsk_yahan_apni_asli_key_dal_do"
        
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://127.0.0.1:11434/api/generate"

    def is_online(self) -> bool:
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("gsk_yahan")

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. Try Online Groq API first if a valid key is provided and net is available
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
                    response = requests.post(self.groq_url, headers=headers, json=payload, timeout=8.0)
                    if response.status_code == 200:
                        data = response.json()
                        return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
                except Exception:
                    pass

        # 2. Automatic Fallback to Local Ollama (Offline Mode) if Groq fails or is unconfigured
        try:
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
            # 60 seconds timeout to safely handle first-time model loading in background
            response = requests.post(self.ollama_url, json=payload, timeout=60.0)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
        except Exception as e:
            pass

        # 3. Final Safety Net if both fail
        return "**[Connection Notice]** Internet band hai aur local Ollama respond nahi kar raha. Baraye meharbani Ollama open rakhein.", "[Error Mode]"
