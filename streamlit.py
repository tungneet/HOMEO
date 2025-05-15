import streamlit as st
import requests

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

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🧪 Connect to App", "👤 User Management", "💬 Chat", "📜 History"])

# -------- TAB 1: Test Connection --------
with tab1:
    st.subheader("Test Connection to Lambda App")
    if st.button("Test Connection"):
        try:
            response = requests.get(TEST_API)
            if response.status_code == 200:
                st.success("Connection successful ✅")
                st.json(response.json())
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")

# -------- TAB 2: User Management --------
with tab2:
    st.subheader("Switch User")
    st.write(f"Current user: {st.session_state.current_user}")
    new_user = st.text_input("Enter new user ID", placeholder="e.g. user_5678")

    if st.button("Switch User"):
        if new_user.strip():
            st.session_state.current_user = new_user.strip()
            st.success(f"Switched to: {st.session_state.current_user}")
        else:
            st.warning("Please enter a valid user ID.")

# -------- TAB 3: Chat --------
with tab3:
    st.subheader("💬 ਕੰਪਾਊਂਡਰ ਨਾਲ ਗੱਲ ਕਰੋ।")
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

# -------- TAB 4: History --------
with tab4:
    st.subheader("Chat History")
    try:
        history_url = f"{HISTORY_API}/{st.session_state.current_user}"
        response = requests.get(history_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("history"):
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