import requests

class LLMRouter:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3" # Ya jo model aapke paas installed ho (jaise llama3:8b)

    def is_online(self) -> bool:
        return False  # Strictly Offline Mode

    def get_response(self, prompt: str) -> tuple[str, str]:
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
            
            response = requests.post(self.ollama_url, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status: {response.status_code}", "[Error Mode]"
                
        except Exception:
            return "⚠️ **Local Ollama is not running.** Please start Ollama on your PC.", "[Error Mode]"
