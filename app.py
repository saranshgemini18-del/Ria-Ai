import streamlit as st
from groq import Groq
import requests
import datetime

# --- CONFIG ---
DB_URL = "https://my-ai-9791f-default-rtdb.firebaseio.com"
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Ria AI", page_icon="💁‍♀️")
system_prompt = {"role": "system", "content": "Tu Ria hai, ek chill Indian bestie. Hinglish mein baat kar. Short aur witty ban."}

# --- SESSION STATES ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_id" not in st.session_state: st.session_state.user_id = None
if "messages" not in st.session_state: st.session_state.messages = [system_prompt]
if "chat_id" not in st.session_state: st.session_state.chat_id = None

# --- AUTH & DB FUNCTIONS ---
def login(u, p):
    res = requests.get(f"{DB_URL}/users/{u}.json").json()
    return True if res and res['pass'] == p else False

def signup(u, p):
    if requests.get(f"{DB_URL}/users/{u}.json").json(): return False
    requests.put(f"{DB_URL}/users/{u}.json", json={"pass": p})
    return True

def get_user_chats(username):
    res = requests.get(f"{DB_URL}/history/{username}.json").json()
    return res if res else {}

# --- SIDEBAR ---
st.sidebar.title("Ria AI 💁‍♀️")

if not st.session_state.logged_in:
    choice = st.sidebar.radio("Login/Signup", ["Login", "Signup"])
    u = st.sidebar.text_input("Username").lower()
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Go"):
        if choice == "Signup":
            if signup(u, p): st.sidebar.success("Account ready!")
            else: st.sidebar.error("User exists!")
        elif login(u, p):
            st.session_state.logged_in, st.session_state.user_id = True, u
            st.rerun()
else:
    st.sidebar.write(f"Hi **{st.session_state.user_id}**! ✨")
    
    # New Chat Button
    if st.sidebar.button("➕ New Chat"):
        st.session_state.messages = [system_prompt]
        st.session_state.chat_id = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Pichli Baatein (History)")
    
    # History List
    user_chats = get_user_chats(st.session_state.user_id)
    for c_id in reversed(list(user_chats.keys())):
        if st.sidebar.button(f"💬 {user_chats[c_id]['title']}", key=c_id):
            st.session_state.messages = [system_prompt] + user_chats[c_id]['msgs']
            st.session_state.chat_id = c_id
            st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- MAIN CHAT INTERFACE ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Bol na yaar..."):
    # First message in new chat creates a Chat ID
    if not st.session_state.chat_id and st.session_state.logged_in:
        st.session_state.chat_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        chat_title = prompt[:20] + "..."
        st.session_state.chat_title = chat_title

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # AI Response
    try:
        model = "llama-3.1-8b-instant" if st.session_state.logged_in else "llama-3.3-70b-versatile"
        res = client.chat.completions.create(model=model, messages=st.session_state.messages[-10:]).choices[0].message.content
    except Exception as e: res = f"Limit hit! {e}"

    with st.chat_message("assistant"): st.markdown(res)
    st.session_state.messages.append({"role": "assistant", "content": res})

    # Save to Firebase if logged in
    if st.session_state.logged_in:
        chat_data = {
            "title": st.session_state.chat_title,
            "msgs": st.session_state.messages[1:] # skip system prompt
        }
        requests.put(f"{DB_URL}/history/{st.session_state.user_id}/{st.session_state.chat_id}.json", json=chat_data)
