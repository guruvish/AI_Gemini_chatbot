import os
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
import speech_recognition as sr
import streamlit.components.v1 as components


if "last_response" not in st.session_state:
    st.session_state.last_response = ""


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
        ['ChatBot',"Voice Assistant", 'Image Captioning', 'Embed text', 'Ask me anything'],
        menu_icon='robot',
        icons=['chat-dots-fill', "mic",'image-fill', 'textarea-t', 'patch-question-fill'],
        default_index=0
    )

if "prev_page" not in st.session_state:
    st.session_state.prev_page = selected

if st.session_state.prev_page != selected:
    st.session_state.prev_page = selected

# Function to translate roles between Gemini and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# ---------- VOICE FUNCTIONS ----------
def voice_to_text():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now")
            audio = r.listen(source, timeout=5)
    except Exception:
        return ""

    try:
        return r.recognize_google(audio)
    except Exception:
        return ""
# -------------------if You want Female Voice ---------------------add this instead -----------#
# def speak_browser(text):
        # st.session_state.last_response = text
#     js_code = f"""
#     <script>
#     var voices = window.speechSynthesis.getVoices();
#     var msg = new SpeechSynthesisUtterance(`{text}`);
#     msg.voice = voices.find(v => v.name.includes('Female')) || voices[0];
#     window.speechSynthesis.speak(msg);
#     </script>
#     """
#     components.html(js_code, height=0)
def speak_browser(text):

    if not text:
        return

    # Escape special characters
    safe_text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

    js_code = f"""
    <script>
    window.speechSynthesis.cancel();

    var msg = new SpeechSynthesisUtterance("{safe_text}");
    msg.lang = "en-US";
    msg.rate = 1;
    msg.pitch = 1;
    msg.volume = 1;

    window.speechSynthesis.speak(msg);
    </script>
    """

    components.html(js_code, height=120)

def stop_browser_speech():
    js_code = """
    <script>
    window.speechSynthesis.cancel();
    </script>
    """
    components.html(js_code, height=0)




def replay_browser_speech():

    text = st.session_state.last_response

    if not text:
        return

    safe_text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

    js_code = f"""
    <script>
    window.speechSynthesis.cancel();

    var msg = new SpeechSynthesisUtterance("{safe_text}");
    msg.lang = "en-US";

    window.speechSynthesis.speak(msg);
    </script>
    """

    components.html(js_code, height=120)



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

            # Save response
            st.session_state.last_response = gemini_response.text

            msg_id = len(st.session_state.chat_session.history)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🔊 Speak", key=f"speak_{msg_id}"):
                    speak_browser(st.session_state.last_response)

            with col2:
                if st.button("🔁 Replay", key=f"replay_{msg_id}"):
                    replay_browser_speech()

            with col3:
                if st.button("🛑 Stop", key=f"stop_{msg_id}"):
                    stop_browser_speech()
# ================= VOICE ASSISTANT =================
elif selected == "Voice Assistant":

    st.title("🎤 Gemini Voice Assistant")
    auto_voice = st.toggle("🔊 Auto Speak")

    if st.button("🎙 Start Listening"):
        text = voice_to_text()

        if text:
            st.write("🗣 You said:", text)

            with st.spinner("Gemini thinking..."):
                response = gemini_text_response(text)

            st.success(response)
            st.session_state.last_response = response

            if auto_voice:
                speak_browser(response)

        else:
            st.warning("Could not recognize speech")

    # Controls always visible
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔊 Speak Response"):
            speak_browser(st.session_state.last_response)

    with col2:
        if st.button("🔁 Replay"):
            replay_browser_speech()
    
    with col3:
        if st.button("🛑 Stop Voice"):
            stop_browser_speech()
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

