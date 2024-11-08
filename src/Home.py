
import streamlit as st
import logging
from main.bot import process_input
import base64

with open("src/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():

    """
    Main function to run the Streamlit interface for the intelligent chat application.

    It initializes the chatbot, manages the conversation history, and handles user input.
    """

    st.markdown('<h1 class="titlehead">Shall We Chat!</h1>', unsafe_allow_html=True)

    user_id = st.session_state.get('user_id', 'guest')
    logging.info(f"Initializing chatbot for user: {user_id}")


    if 'history' not in st.session_state:
        st.session_state['history'] = []
        logging.info("Conversation history initialized.")

    logging.info("Displaying conversation history.")
    for interaction in st.session_state['history']:
        st.write(f"**You:** {interaction['user_input']}")
        st.write(f"**Chat:** {interaction['response']}")

    user_input = st.text_input("Type your question:")
    if user_input:
        logging.info(f"User typed: {user_input}")
        response = process_input(user_input)
        st.session_state['history'].append({"user_input": user_input, "response": response})
        st.session_state.query_params = {'user_input': user_input}

        logging.info(f"Chatbot response: {response}")

        st.write(response)


def get_img_as_base64(file):
    """
    Convert an image file to a base64 encoded string for use as a background image.

    Args:
        file (str): The path to the image file.

    Returns:
        str: The base64 encoded string representation of the image.
    """
    with open(file,'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("src/image.jpg")


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
