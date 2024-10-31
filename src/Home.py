
import streamlit as st
import logging
from main.bot import Chatbot
import base64

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():


    # Login screen
    if 'user_id' not in st.session_state:
        st.markdown('<h1 class="title">Welcome to our space!</h1>', unsafe_allow_html=True)
        username = st.text_input("Username:")
        if st.button("Log In"):
            st.session_state['user_id'] = username
            st.session_state['session_id'] = st.session_state.get('session_id', 0) + 1
            st.success(f"Welcome, {username}.Click again and have fun!")
            logging.info(f"User {username} logged in with session ID {st.session_state['session_id']}")
            st.markdown('</div>', unsafe_allow_html=True)
        return

    user_id = st.session_state['user_id']
    chatbot = Chatbot(user_id)

    # # #Response tone selection
    st.markdown('<h1 class="title">How can I assist you today!</h1>', unsafe_allow_html=True)
    tone_choice = st.radio("Select response tone:", ["***Formal***", "***Informal***"], index=0 if chatbot.response_tone == "Informal" else 1)
    if tone_choice != chatbot.response_tone:
        chatbot.set_response_tone(tone_choice)
        st.success(f"Tone preference '{tone_choice}' saved.")
        logging.info(f"User {user_id} set response tone to: {tone_choice}")

    # Request user input
    user_input = st.text_input("Let's chat!")
    if user_input:
        response = chatbot.process_input(user_input)
        st.write(response)
        logging.info(f"Processed input for user {user_id}: {user_input}")

    # Logout button
    if st.button("Log Out"):
        # Clear session state
        st.session_state.clear()
        st.success("Are you leaving? Click again and see you later!")
        logging.info(f"User {user_id} logged out.")
        st.stop()
    st.markdown('</div>', unsafe_allow_html=True)

def get_img_as_base64(file):
    with open(file,'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")


st.markdown(
    f"""
    <style>
    .stAppViewContainer {{
        background-image: url("data:image/jpg;base64,{img}");
        background-size: cover;
        background-position: 20%;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()
