import requests

class LLMRouter:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"

    def is_online(self) -> bool:
        return False

    def get_response(self, prompt: str) -> tuple[str, str]:
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            # Timeout extended to 180 seconds (3 minutes) to handle heavy PDF context processing locally
            response = requests.post(self.ollama_url, json=payload, timeout=180.0)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status Code: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return f"**[Connection Error]** Details: {str(e)}", "[Error Mode]"
