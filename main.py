import os
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu

from gemini_utility import (
    load_gemini_model,
    gemini_text_response,
    gemini_vision_response,
    embeddings_model_response
)

working_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Gemini AI",
    page_icon="🧠",
    layout="centered",
)

with st.sidebar:
    selected = option_menu(
        'Gemini AI',
        ['ChatBot', 'Image Captioning', 'Embed text', 'Ask me anything'],
        menu_icon='robot',
        icons=['chat-dots-fill', 'image-fill', 'textarea-t', 'patch-question-fill'],
        default_index=0
    )


# Function to translate roles between Gemini and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# ---------------- CHATBOT ----------------
if selected == 'ChatBot':

    model = load_gemini_model()

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    st.title("🤖 ChatBot")

    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    user_prompt = st.chat_input("Ask Gemini...")

    if user_prompt:
        st.chat_message("user").markdown(user_prompt)

        gemini_response = st.session_state.chat_session.send_message(user_prompt)

        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)


# ---------------- IMAGE CAPTIONING ----------------
if selected == "Image Captioning":

    st.title("📷 Snap Narrate")

    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if uploaded_image and st.button("Generate Caption"):

        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            resized_img = image.resize((800, 500))
            st.image(resized_img)

        default_prompt = "Write a short caption for this image"

        caption = gemini_vision_response(default_prompt, image)

        with col2:
            st.info(caption)


# ---------------- EMBEDDINGS ----------------
if selected == "Embed text":

    st.title("🔡 Embed Text")

    user_prompt = st.text_area('', placeholder="Enter the text to get embeddings")

    if st.button("Get Embedding"):
        response = embeddings_model_response(user_prompt)
        st.write(response)


# ---------------- ASK ANYTHING ----------------
if selected == "Ask me anything":

    st.title("❓ Ask me a question")

    user_prompt = st.text_area('', placeholder="Ask me anything...")

    if st.button("Get Response"):
        response = gemini_text_response(user_prompt)
        st.markdown(response)