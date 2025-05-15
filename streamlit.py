import streamlit as st
import requests
import openai
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import tempfile
import queue

# -------------------- CONFIG --------------------
# API endpoints
BASE_URL = "https://2o02845p39.execute-api.ap-south-1.amazonaws.com/plane_BA"
CHAT_API = f"{BASE_URL}/chat"
HISTORY_API = f"{BASE_URL}/history"
TEST_API = f"{BASE_URL}/test"

# OpenAI API Key
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-api-key-here")  # Replace or set via secrets

# App settings
st.set_page_config(page_title="German Homeopathy Clinic", layout="centered")
st.markdown("<h1 style='text-align: center; color: green;'>German Homeopathy Clinic by Hardev Singh</h1>", unsafe_allow_html=True)

# Session state
if "current_user" not in st.session_state:
    st.session_state.current_user = "user_1234"
if "user_msg" not in st.session_state:
    st.session_state.user_msg = ""

# -------------------- SIDEBAR NAV --------------------
sidebar_choice = st.sidebar.radio(
    "Navigate",
    ("🧪 Connect to App", "👤 User Management", "📜 History"),
    index=0
)

# -------------------- MAIN CHAT --------------------
st.subheader("💬 ਕੰਪਾਊਂਡਰ ਨਾਲ ਗੱਲ ਕਰੋ।")

# Microphone input section
st.markdown("**ਮਾਈਕ ਰਾਹੀਂ ਗੱਲ ਕਰੋ (Speak using mic):**")

audio_queue = queue.Queue()

class AudioProcessor:
    def __init__(self):
        self.audio_buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().tobytes()
        audio_queue.put(pcm)
        return frame

webrtc_ctx = webrtc_streamer(
    key="mic",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    client_settings=ClientSettings(media_stream_constraints={"audio": True, "video": False}),
    audio_receiver_size=256,
    rtc_configuration={},
    sendback_audio=False,
    audio_frame_callback=AudioProcessor().recv,
)

if st.button("🎙️ Transcribe Mic Audio"):
    if not audio_queue.empty():
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            audio_data = b"".join(list(audio_queue.queue))
            temp_audio.write(audio_data)
            audio_path = temp_audio.name

        with st.spinner("Transcribing..."):
            try:
                with open(audio_path, "rb") as f:
                    transcript = openai.Audio.transcribe("whisper-1", f)
                    st.session_state.user_msg = transcript['text']
                    st.success(f"Recognized: {transcript['text']}")
            except Exception as e:
                st.error(f"Whisper failed: {str(e)}")
    else:
        st.warning("No audio captured. Try speaking after enabling mic.")

# Text input
user_msg = st.text_area("ਤੁਹਾਡੀ ਤਬੀਅਤ ਬਾਰੇ ਇੱਥੇ ਲਿਖੋ।", value=st.session_state.user_msg)
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

# -------------------- SIDEBAR TABS --------------------
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
