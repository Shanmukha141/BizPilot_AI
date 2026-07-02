import streamlit as st
import requests
import uuid

# Configuration
FLASK_BACKEND_URL = "http://127.0.0.1:5000/api/chat"

# Page Setup
st.set_page_config(page_title="BizPilot AI", page_icon="👔", layout="centered")
st.title("BizPilot AI 👔")
st.caption("Autonomous Business Operations Copilot")

# Initialize session state for memory and unique session IDs
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask BizPilot to calculate something or check the date..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the Flask Backend
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                payload = {
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                    "history": st.session_state.messages
                }
                response = requests.post(FLASK_BACKEND_URL, json=payload)
                response_data = response.json()

                if response.status_code == 200:
                    assistant_reply = response_data["response"]
                    st.markdown(assistant_reply)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                else:
                    st.error(f"Error: {response_data.get('error', 'Unknown error')}")
            
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is your Flask server running?")