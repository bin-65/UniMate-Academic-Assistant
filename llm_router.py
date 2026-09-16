import os
import requests
import google.generativeai as genai

class LLMRouter:
    def __init__(self):
        # Google AI Studio API Key setup
        self.api_key = os.environ.get("GEMINI_API_KEY", "") 
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_enabled = True
            except:
                self.gemini_enabled = False
        else:
            self.gemini_enabled = False
            
        self.gemini_model_name = "gemini-1.5-flash"
        
        # Local Ollama fallback setup
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.ollama_model_name = "llama3:latest"

    def is_online(self) -> bool:
        # Returns True if online Gemini key is available
        return self.gemini_enabled

    def get_response(self, prompt: str) -> tuple[str, str]:
        # 1. Pehle Online Gemini API try karega agar key maujood hai
        if self.api_key:
            try:
                model = genai.GenerativeModel(self.gemini_model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text, "[Online Mode (Google Gemini)]"
            except Exception as e:
                # Agar online fail ho jaye, toh neechay local Ollama par chala jayega
                pass

        # 2. Offline Fallback: Local Ollama
        try:
            payload = {
                "model": self.ollama_model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 512,
                    "num_ctx": 2048,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', ''), "[Offline Mode (Ollama)]"
        except Exception as e:
            pass

        # Agar dono fail ho jayein
        return "⚠️ **Connection Error:** Neither Online Gemini API nor Local Ollama is responding. Please check your internet or start Ollama.", "[Error Mode]"
