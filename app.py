import streamlit as st
from groq import Groq
import firebase_admin
from firebase_admin import credentials, firestore
import json

# 1. Firebase Setup (Ria ki Memory)
if not firebase_admin._apps:
    # Streamlit Secrets se JSON uthayega
    try:
        key_dict = json.loads(st.secrets["firebase"]["json_key"])
        creds = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(creds)
    except Exception as e:
        st.error(f"Firebase setup mein error hai bhai: {e}")

db = firestore.client()

# 2. Groq AI Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("Ria AI - Teri Chill Bestie 💁‍♀️")

# 3. User Pehchan (Simple Login/Name input)
user_name = st.sidebar.text_input("Tera Naam Kya Hai?", "Guest")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. AI Se Baat Karne Ka Logic
def get_ria_response():
    try:
        # Chota model use kar rahe hain taaki Rate Limit error na aaye
        completion = client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=st.session_state.messages[-5:] # Sirf last 10 baatein
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Arre yaar, dimag thak gaya mera! (Error: {e})"

# 5. UI Layout
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

    # 6. Database mein Save karna (Memory)
    try:
        db.collection("chats").document(user_name).collection("history").add({
            "prompt": prompt,
            "response": response
        })
    except:
        pass # Agar database fail ho toh chat chalti rahe