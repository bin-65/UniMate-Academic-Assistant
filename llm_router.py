import requests

class LLMRouter:
    def __init__(self):
        # Local Ollama endpoint
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3"

    def is_online(self) -> bool:
        # Forcing local offline mode using pure synchronous requests to avoid Windows asyncio socket bugs
        return False

    def get_response(self, prompt: str) -> tuple[str, str]:
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            # Pure synchronous post request - 100% stable on Windows, zero WinError 10054
            response = requests.post(self.ollama_url, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status Code: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return f"**[Connection Error]** Ollama server tak request nahi gayi. Details: {str(e)}", "[Error Mode]"
