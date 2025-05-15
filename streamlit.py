import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
import openai
import io

# API endpoints
BASE_URL = "https://2o02845p39.execute-api.ap-south-1.amazonaws.com/plane_BA"
CHAT_API = f"{BASE_URL}/chat"
HISTORY_API = f"{BASE_URL}/history"
TEST_API = f"{BASE_URL}/test"

# Set OpenAI API key (replace with your key)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

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

# Main area always shows Chat tab
st.subheader("💬 ਕੰਪਾਊਂਡਰ ਨਾਲ ਗੱਲ ਕਰੋ।")

# Audio recorder widget
audio_bytes = audio_recorder(text="ਮਾਈਕ ਚਾਲੂ ਕਰੋ, 2 ਸਕਿੰਟ ਬਾਅਦ ਰਿਕਾਰਡਿੰਗ ਸ਼ੁਰੂ ਹੋਵੇਗੀ...", recording_time=5000)

# When audio is recorded, send to Whisper for transcription
user_msg = ""
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    with st.spinner("Processing audio with Whisper..."):
        try:
            audio_file = io.BytesIO(audio_bytes)
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            user_msg = transcript.get("text", "")
            st.success(f"Transcribed Text: {user_msg}")
        except Exception as e:
            st.error(f"Whisper transcription error: {str(e)}")

# Also allow manual text input, prefill with transcribed text if available
user_msg_input = st.text_area("ਤੁਹਾਡੀ ਤਬੀਅਤ ਬਾਰੇ ਇੱਥੇ ਲਿਖੋ।", value=user_msg)

if st.button("Send Message"):
    if user_msg_input.strip():
        payload = {
            "user_id": st.session_state.current_user,
            "user_message": user_msg_input.strip()
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

# Render sidebar tabs content
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
