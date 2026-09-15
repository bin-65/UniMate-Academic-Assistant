import os
import requests

class LLMRouter:
    def __init__(self):
        # Yahan apni real Groq API key dal dein agar online chalana hai
        # Agar yeh placeholder rahe ga, toh app automatically offline Ollama par chalegi
        self.groq_api_key = "gsk_yahan_apni_asli_key_dal_do"
        
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"

    def is_online(self) -> bool:
        return bool(self.groq_api_key) and not self.groq_api_key.startswith("gsk_yahan")

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. ONLINE MODE: Agar Groq API key di ho aur net active ho
        if self.is_online():
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            models_to_try = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
            
            for model_name in models_to_try:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You are UniMate, an expert academic assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
                try:
                    response = requests.post(self.groq_url, headers=headers, json=payload, timeout=15.0)
                    if response.status_code == 200:
                        data = response.json()
                        return data['choices'][0]['message']['content'], "[Online Mode (Groq)]"
                except Exception:
                    pass

        # 2. OFFLINE MODE: Local Ollama (Unlimited queries, zero cost, local privacy)
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 512,      # Response length limit taake bar bar heavy load na paray
                    "num_ctx": 2048,         # Context window fix taake memory overflow ya timeout na ho
                    "temperature": 0.7
                }
            }
            
            # 120 seconds timeout for heavy sequential local queries
            response = requests.post(self.ollama_url, json=payload, timeout=120.0)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return f"**[Connection Error]** Ollama respond nahi kar raha. Check karein ke black terminal khula hai. Details: {str(e)}", "[Error Mode]"
