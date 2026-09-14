import streamlit as st
from llm_router import LLMRouter

st.set_page_config(page_title="UniMate AI Assistant", page_icon="🎓", layout="wide")

st.title("🎓 UniMate Academic Assistant")
st.caption("Hybrid Online/Offline AI Assistant")

router = LLMRouter()

# Display current connection status badge
if router.is_online():
    st.success("🟢 System Status: Online (Groq API Ready)")
else:
    st.warning("🟡 System Status: Offline (Local Fallback Active)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask UniMate anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response, mode_tag = router.get_response(prompt)
        full_response = f"{response}\n\n`{mode_tag}`"
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
