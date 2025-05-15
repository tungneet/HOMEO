import streamlit as st
import requests
import time
from audiorecorder import audiorecorder
import openai
import io

# Set your OpenAI API key here or via environment variable OPENAI_API_KEY
openai.api_key = st.secrets.get("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY"

# API endpoints
BASE_URL = "https://2o02845p39.execute-api.ap-south-1.amazonaws.com/plane_BA"
CHAT_API = f"{BASE_URL}/chat"
HISTORY_API = f"{BASE_URL}/history"
TEST_API = f"{BASE_URL}/test"

# App settings
st.set_page_config(page_title="German Homeopathy Clinic", layout="centered")
st.markdown("<h1 style='text-align: center; color: green;'>German Homeopathy Clinic by Hardev Singh</h1>", unsafe_allow_html=True)

# Persistent session state for current user
if "current_user" not in st.session_state:
    st.session_state.current_user = "user_1234"

# Sidebar tabs (except chat)
sidebar_choice = st.sidebar.radio(
    "Navigate",
    ("🧪 Connect to App", "👤 User Management", "📜 History"),
    index=0
)

# ----- Sidebar content -----
if sidebar_choice == "🧪 Connect to App":
    st.sidebar.subheader("Test Connection to Lambda App")
    if st.sidebar.button("Test Connection"):
        try:
            response = requests.get(TEST_API)
            if response.status_code == 200:
                st.sidebar.success("Connection successful ✅")
                st.sidebar.json(response.json())
            else:
                st.sidebar.error(f"Error: {response.status_code}")
                st.sidebar.text(response.text)
        except Exception as e:
            st.sidebar.error(f"Connection failed: {str(e)}")

elif sidebar_choice == "👤 User Management":
    st.sidebar.subheader("Switch User")
    st.sidebar.write(f"Current user: `{st.session_state.current_user}`")
    new_user = st.sidebar.text_input("Enter new user ID", placeholder="e.g. user_5678")

    if st.sidebar.button("Switch User"):
        if new_user.strip():
            st.session_state.current_user = new_user.strip()
            st.sidebar.success(f"Switched to: `{st.session_state.current_user}`")
        else:
            st.sidebar.warning("Please enter a valid user ID.")

elif sidebar_choice == "📜 History":
    st.sidebar.subheader("Fetch Chat History")
    if st.sidebar.button("Get History"):
        try:
            history_url = f"{HISTORY_API}/{st.session_state.current_user}"
            response = requests.get(history_url)
            if response.status_code == 200:
                data = response.json()
                if data.get("history"):
                    st.subheader(f"Chat History for `{st.session_state.current_user}`")
                    for item in data["history"]:
                        st.markdown(f"**You:** {item.get('user_message', '')}")
                        st.markdown(f"**Assistant:** {item.get('assistant_response', '')}")
                        st.markdown("---")
                else:
                    st.info("No history found for this user.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to fetch history: {str(e)}")

# ----- Main area: Chat + Mic with STT -----
st.subheader("💬 ਕੰਪਾਊਂਡਰ ਨਾਲ ਗੱਲ ਕਰੋ।")

# 2-second auto mic delay logic
if "wait_start" not in st.session_state:
    st.session_state.wait_start = True
    st.session_state.wait_start_time = time.time()

if st.session_state.wait_start:
    elapsed = time.time() - st.session_state.wait_start_time
    st.write("🎙️ ਮਾਈਕ 2 ਸਕਿੰਟ ਵਿੱਚ ਸ਼ੁਰੂ ਹੋ ਜਾਵੇਗਾ ...")
    if elapsed > 2:
        st.session_state.wait_start = False
        st.experimental_rerun()

if not st.session_state.wait_start:
    # Show audiorecorder widget
    audio = audiorecorder("ਮਾਈਕ ਚਾਲੂ ਕਰੋ", "Recording...")

    if len(audio) > 0:
        st.audio(audio.tobytes(), format="audio/wav")
        with st.spinner("ਅਕਸ਼ਰ ਬਦਲ ਰਹੇ ਹਾਂ (Transcribing)..."):
            # convert audio bytes to file-like object
            audio_file = io.BytesIO(audio.tobytes())

            try:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                user_msg = transcript["text"]
                st.success(f"ਟ੍ਰਾਂਸਕ੍ਰਿਪਟ: {user_msg}")

                # Prepare payload and send chat message automatically
                payload = {
                    "user_id": st.session_state.current_user,
                    "user_message": user_msg.strip()
                }
                response = requests.post(CHAT_API, json=payload)
                if response.status_code == 200:
                    res = response.json()
                    if "response" in res:
                        st.markdown("**ਸਹਾਇਕ ਦੀ ਜਵਾਬ:**")
                        st.success(res["response"])
                    else:
                        st.error(f"Error: {res.get('error', 'Unknown error')}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"ਟ੍ਰਾਂਸਕ੍ਰਿਪਸ਼ਨ ਵਿੱਚ ਸਮੱਸਿਆ: {str(e)}")

else:
    # Also allow manual text input & send message button below mic UI
    user_msg = st.text_area("ਤੁਹਾਡੀ ਤਬੀਅਤ ਬਾਰੇ ਇੱਥੇ ਲਿਖੋ।")

    if st.button("Send Message"):
        if user_msg.strip():
            payload = {
                "user_id": st.session_state.current_user,
                "user_message": user_msg.strip()
            }
            try:
                response = requests.post(CHAT_API, json=payload)
                if response.status_code == 200:
                    res = response.json()
                    if "response" in res:
                        st.markdown("**Assistant Response:**")
                        st.success(res["response"])
                    else:
                        st.error(f"Error: {res.get('error', 'Unknown error')}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {str(e)}")
        else:
            st.warning("Message cannot be empty.")
