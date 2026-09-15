import json
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
                "stream": True,  # <--- Yeh line timeout ko hamesha ke liye khatam kar degi
                "options": {
                    "num_predict": 512,
                    "num_ctx": 2048,
                    "temperature": 0.7
                }
            }
            
            # stream=True ki waja se connection live rahega aur data chunk by chunk aayega
            response = requests.post(self.ollama_url, json=payload, stream=True, timeout=60.0)
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        full_response += data.get('response', '')
                        if data.get('done', False):
                            break
                return full_response, "[Offline Mode (Ollama)]"
            else:
                return f"**[Ollama Error]** Status: {response.status_code}", "[Error Mode]"
                
        except Exception as e:
            return f"**[Connection Error]** Details: {str(e)}", "[Error Mode]"
