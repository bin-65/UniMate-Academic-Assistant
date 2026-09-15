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
                "stream": False,
                "options": {
                    "num_predict": 512,
                    "num_ctx": 2048,
                    "temperature": 0.7
                }
            }
            
            # timeout=None ka matlab hai ke connection kabhi timeout nahi hoga, 
            # Python tab tak wait karega jab tak Ollama khud jawab wapas na bhej de!
            response = requests.post(self.ollama_url, json=payload, timeout=None)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return f"**[Connection Error]** Details: {str(e)}", "[Error Mode]"
