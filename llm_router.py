import requests
import json

class LLMRouter:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.model_name = "llama3:latest"

    def is_online(self) -> bool:
        return False  # Strictly Offline Mode

    def get_response(self, prompt: str) -> tuple[str, str]:
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,  # Filhal error se bachne ke liye False rakha hai
                "options": {
                    "num_predict": 512,
                    "num_ctx": 2048,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return f"⚠️ **Local Ollama connection failed:** {str(e)}", "[Error Mode]"
