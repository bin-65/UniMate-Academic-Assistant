import os
import requests

class LLMRouter:
    def __init__(self):
        # Local Ollama configuration
        self.ollama_url = "http://127.0.0.1:11434/api/generate"

    def is_online(self) -> bool:
        # Force local offline mode to ensure smooth performance without API key issues
        return False

    def get_response(self, prompt: str) -> tuple[str, str]:
        # Direct call to local Ollama (llama3)
        try:
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status Code: {response.status_code}", "[Error Mode]"
        except Exception as e:
            return f"**[Connection Error]** Could not connect to local Ollama. Please ensure Ollama app is open. Details: {str(e)}", "[Error Mode]"
