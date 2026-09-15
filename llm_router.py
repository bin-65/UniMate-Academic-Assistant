import requests

class LLMRouter:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3:latest"

    def is_online(self) -> bool:
        return False  # Strictly Offline Mode

    def check_ollama_running(self) -> bool:
        """Pehle se check karta hai ke Ollama server active hai ya nahi"""
        try:
            # Ollama ka base status endpoint ping karte hain
            response = requests.get("http://localhost:11434/", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def get_response(self, prompt: str) -> tuple[str, str]:
        # Pehle check karo ke Ollama chal bhi raha hai ya nahi
        if not self.check_ollama_running():
            return "⚠️ **Local Ollama is not running.** Please start Ollama on your PC.", "[Error Mode]"

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
