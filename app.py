import streamlit as st
from groq import Groq
import requests
import datetime
from streamlit_google_auth import Authenticate

# --- 1. CONFIG & AUTH SETUP ---
DB_URL = "https://my-ai-9791f-default-rtdb.firebaseio.com"
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Google Login Setup
authenticator = Authenticate(
    client_id=st.secrets["google_client_id"],
    client_secret=st.secrets["google_client_secret"],
    redirect_uri="https://friendai.streamlit.app", # Jo file mein hai wahi dalo
    cookie_name='ria_auth_cookie',
    cookie_key='ria_signature_key',
    cookie_expiry_days=30,
)
# Authentication check
authenticator.check_authenticity()

# System Persona
system_prompt = {"role": "system", "content": "Tu Ria hai, ek chill Indian bestie. Hinglish mein baat kar. Short aur witty ban. 'Bro' aur 'Yaar' touch rakh."}

# --- 2. SIDEBAR & LOGIN LOGIC ---
if not st.session_state.get('connected'):
    st.title("Ria AI - Teri Bestie 💁‍♀️")
    st.write("Bhai, pehle Google se login toh kar le, fir baatein karenge!")
    authenticator.login()
    st.stop()

# Agar connected hai toh user ka data nikal lo
user_info = st.session_state['user_info']
u_name = user_info['name']
u_email = user_info['email'].replace(".", "_") # Firebase dot nahi leta

st.sidebar.image(user_info['picture'], width=80)
st.sidebar.write(f"Kaisi hai meri jaan, **{u_name}**? ✨")

# --- 3. SESSION STATES & HISTORY ---
if "messages" not in st.session_state: st.session_state.messages = [system_prompt]
if "chat_id" not in st.session_state: st.session_state.chat_id = None

# History fetch function
def get_user_chats(email):
    res = requests.get(f"{DB_URL}/history/{email}.json").json()
    return res if res else {}

# New Chat Button
if st.sidebar.button("➕ New Chat"):
    st.session_state.messages = [system_prompt]
    st.session_state.chat_id = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Pichli Baatein")

# Show History List
user_chats = get_user_chats(u_email)
for c_id in reversed(list(user_chats.keys())):
    if st.sidebar.button(f"💬 {user_chats[c_id]['title']}", key=c_id):
        st.session_state.messages = [system_prompt] + user_chats[c_id]['msgs']
        st.session_state.chat_id = c_id
        st.rerun()

if st.sidebar.button("Logout"):
    authenticator.logout()
    st.rerun()

# --- 4. CHAT INTERFACE ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Bol na yaar..."):
    # Create session if new
    if not st.session_state.chat_id:
        st.session_state.chat_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.chat_title = prompt[:20] + "..."

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Groq Response (Using Llama 3.1 8B for logged in users)
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=st.session_state.messages[-10:]
        ).choices[0].message.content
    except Exception as e: res = f"Limit hit yaar! {e}"

    with st.chat_message("assistant"): st.markdown(res)
    st.session_state.messages.append({"role": "assistant", "content": res})

    # Save to Firebase
    chat_data = {
        "title": st.session_state.chat_title,
        "msgs": st.session_state.messages[1:]
    }
    requests.put(f"{DB_URL}/history/{u_email}/{st.session_state.chat_id}.json", json=chat_data)
