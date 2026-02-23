import streamlit as st
from groq import Groq

# Header jo terminal jaisa dikhe
st.markdown("### < SYSTEM: FRIEND_LINK_INITIALIZED >")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception as e:
    st.error("Bhai, API Key nahi mil rahi! Streamlit Settings mein check kar.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Ria, a chill Indian female best friend. Use Hinglish and emojis. Keep it fun! 🚀"}
    ]

# Chat display
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# User input
if prompt := st.chat_input("GUEST@LOCAL_HOST:~ $"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Response logic
    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.messages
        )
        reply = completion.choices[0].message.content
        st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
