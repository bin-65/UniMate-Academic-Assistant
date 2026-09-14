import os
import requests

class LLMRouter:
    def __init__(self):
        # Yahan apni asli Groq API key direct paste kar dein
        self.groq_api_key = "gsk_yahan_apni_asli_key_dal_do"
            
        print(f"DEBUG: Key Loaded -> {self.groq_api_key[:6]}... (Length: {len(self.groq_api_key)})")
            
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
                    print(f"Trying Groq Model '{model_name}' -> Status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
                    else:
                        print(f"Error Response: {response.text}")
                except Exception as e:
                    print(f"Exception with {model_name}: {str(e)}")

        # Fallback to Ollama if all Groq attempts fail
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

        return "**[Connection Error]** Groq API key appears invalid or unauthorized. Please generate a fresh key from Groq Console.", "[Error Mode]"
