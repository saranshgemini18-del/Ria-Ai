import streamlit as st
from groq import Groq
import requests
import json

# 1. Groq Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. Firebase URL (Tera wala)
DB_URL = "https://my-ai-9791f-default-rtdb.firebaseio.com"

st.title("Ria AI - Chill Bestie 💁‍♀️")

# Sidebar mein user ka naam
user_name = st.sidebar.text_input("Tera Naam?", "Guest").strip().replace(" ", "_")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Chat Logic
def get_ria_response():
    try:
        # Chota model use kar rahe hain taaki Rate Limit na aaye
        completion = client.chat.completions.create(
            model="llama-3-1-8b-instant", 
            messages=st.session_state.messages[-5:]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Arre yaar, dimag thak gaya! (Wait kar thoda): {e}"

# UI Layout
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Bol na bhai..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ria ka Reply
    response = get_ria_response()
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # 4. Database mein Save karna (Simple & Fast)
    try:
        chat_data = {"user": prompt, "ria": response}
        requests.post(f"{DB_URL}/chats/{user_name}.json", json=chat_data)
    except:
        pass
