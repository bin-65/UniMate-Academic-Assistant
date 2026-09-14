import os
import sys
import streamlit as st

# Ensure root directory is in python path for Streamlit Cloud imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from connection_checker import is_connected
except ImportError:
    from connection_checker import check_internet_connection as is_connected

class LLMRouter:
    def __init__(self):
        self.api_key = self._get_api_key()

    def _get_api_key(self):
        # 1. Try Streamlit Secrets safely
        try:
            if "GROQ_API_KEY" in st.secrets:
                return st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

        # 2. Fallback to Environment Variable
        return os.getenv("GROQ_API_KEY", None)

    def is_online(self):
        """
        Returns True only if an internet connection is available AND an API key exists.
        """
        return is_connected() and bool(self.api_key)

    def get_response(self, prompt):
        if self.is_online():
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content, "[Online Mode]"
            except Exception as e:
                return f"Online API Error: {str(e)}. Falling back to offline mode.", "[Offline Mode]"
        else:
            # Local / Offline Fallback Execution
            return f"Processed request offline: '{prompt}'", "[Offline Mode]"
