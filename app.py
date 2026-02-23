import streamlit as st
from groq import Groq
import requests
import json

# --- 1. CONFIGURATION ---
# Model ko Llama 3.2 rakha hai kyunki ye fast aur active hai
MODEL_NAME = "llama-3.2-3b-preview"
DB_URL = "https://my-ai-9791f-default-rtdb.firebaseio.com"

# --- 2. SETUP & INITIALIZATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Ria AI", page_icon="💁‍♀️")
st.title("Ria AI - Teri Chill Bestie 💁‍♀️")

# Sidebar for User Profile
st.sidebar.title("Ria's Settings")
user_name = st.sidebar.text_input("Tera Naam?", "Guest").strip().replace(" ", "_")

# System Instruction: Ria ki Personality
system_prompt = {
    "role": "system",
    "content": "Tu Ria hai, ek chill Indian best friend. Tera style desi aur cool hai. Hinglish mein baat kar. Short, witty answers de. Emoji use kar. 'Bro' aur 'Yaar' wala touch rakh. Tu hamesha supportive aur funny rehti hai."
}

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]

# --- 3. FUNCTIONS ---
def get_ria_response():
    try:
        # Sirf aakhri 6 messages bhej rahe hain taaki Rate Limit na aaye
        chat_context = [st.session_state.messages[0]] + st.session_state.messages[-5:]
        
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=chat_context,
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Arre yaar, dimag thak gaya! Thoda wait kar le: {str(e)}"

def save_to_firebase(user, prompt, response):
    try:
        chat_data = {
            "user": prompt,
            "ria": response
        }
        # Realtime Database mein data push karna
        requests.post(f"{DB_URL}/chats/{user}.json", json=chat_data)
    except Exception as e:
        print(f"Firebase Error: {e}")

# --- 4. CHAT INTERFACE ---

# Purani chats dikhana (system prompt ko chhupakar)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Bol na bhai..."):
    # User message add karo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ria ka reply generate karo
    with st.chat_message("assistant"):
        response = get_ria_response()
        st.markdown(response)
    
    # History update karo
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Database mein save karo
    save_to_firebase(user_name, prompt, response)

st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: **{user_name}**")
