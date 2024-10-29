
import streamlit as st
import logging
from main.bot import Chatbot

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    st.title("Interactive Chatbot")

    # Login screen
    if 'user_id' not in st.session_state:
        st.subheader("Login")
        username = st.text_input("Username:")
        if st.button("Log In"):
            st.session_state['user_id'] = username
            st.session_state['session_id'] = st.session_state.get('session_id', 0) + 1
            st.success(f"Welcome, {username}!")
            logging.info(f"User {username} logged in with session ID {st.session_state['session_id']}")
        return

    user_id = st.session_state['user_id']
    chatbot = Chatbot(user_id)

    # Response tone selection
    st.subheader("Response Tone Preference")
    tone_choice = st.radio("Select response tone:", ["formal", "informal"], index=0 if chatbot.response_tone == "informal" else 1)
    if st.button("Save Tone Preference"):
        chatbot.set_response_tone(tone_choice)
        st.success(f"Tone preference '{tone_choice}' saved.")
        logging.info(f"User {user_id} set response tone to: {tone_choice}")

    # Request user input
    user_input = st.text_input("Type your statement or question:")
    if user_input:
        response = chatbot.process_input(user_input)
        st.write("Chatbot:", response)
        logging.info(f"Processed input for user {user_id}: {user_input}")

    # Logout button
    if st.button("Log Out"):
        # Clear session state
        st.session_state.clear()
        st.success("You have been logged out.")
        logging.info(f"User {user_id} logged out.")

if __name__ == "__main__":
    main()
