import groq
import ollama
from typing import Tuple
from config import GROQ_API_KEY, GROQ_MODEL, LOCAL_MODEL, SYSTEM_PROMPT_GUARDRAILS

class LLMRouter:
    def __init__(self):
        self.groq_client = groq.Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    def query(self, prompt: str, context: str, is_online: bool) -> Tuple[str, str]:
        formatted_prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}" if context else prompt

        if is_online and self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_GUARDRAILS},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=0.1
                )
                return response.choices[0].message.content, "Groq Cloud AI (Online)"
            except Exception:
                pass

        try:
            response = ollama.chat(
                model=LOCAL_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_GUARDRAILS},
                    {"role": "user", "content": formatted_prompt}
                ],
                options={"temperature": 0.1}
            )
            return response['message']['content'], "Local AI / Ollama (Offline)"
        except Exception as err:
            return f"Execution error: Local model unavailable ({str(err)}). Ensure Ollama is running.", "Offline Engine Error"
