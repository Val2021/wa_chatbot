import streamlit as st

import base64

with open("src/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="title">We are friends of the planet!</h1>', unsafe_allow_html=True)

def get_img_as_base64(file):
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
