import streamlit as st
import requests

# API endpoints
CHAT_API = "https://2o02845p39.execute-api.ap-south-1.amazonaws.com/plane_BA/chat"
HISTORY_API_TEMPLATE = "https://2o02845p39.execute-api.ap-south-1.amazonaws.com/plane_BA/history/{user_id}"

# App title
st.set_page_config(page_title="German Homeopathy Clinic", layout="centered")
st.markdown("<h1 style='text-align: center; color: green;'>German Homeopathy Clinic by Hardev Singh</h1>", unsafe_allow_html=True)

# User inputs
user_id = st.text_input("Enter your User ID", key="user_id")
user_message = st.text_area("Type your message to the assistant", key="user_msg")

# Submit message
if st.button("Send Message"):
    if user_id and user_message:
        payload = {
            "user_id": user_id,
            "user_message": user_message
        }
        try:
            response = requests.post(CHAT_API, json=payload)
            if response.status_code == 200:
                result = response.json()
                st.success("Assistant Response:")
                st.markdown(f"> {result.get('assistant_response', 'No response')}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {str(e)}")
    else:
        st.warning("Please enter both User ID and Message.")

# Fetch chat history
if st.button("Show Chat History"):
    if user_id:
        try:
            history_url = HISTORY_API_TEMPLATE.format(user_id=user_id)
            response = requests.get(history_url)
            if response.status_code == 200:
                data = response.json()
                if "history" in data:
                    st.subheader("Chat History")
                    for item in data["history"]:
                        st.markdown(f"**You**: {item.get('user_message', '')}")
                        st.markdown(f"**Assistant**: {item.get('assistant_response', '')}")
                        st.markdown("---")
                else:
                    st.warning("No chat history found.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to fetch history: {str(e)}")
    else:
        st.warning("Please enter your User ID first.")
