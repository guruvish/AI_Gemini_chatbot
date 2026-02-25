import os
import json
from PIL import Image

import google.generativeai as genai

# working directory path
working_dir = os.path.dirname(os.path.abspath(__file__))

# path of config_data file
config_file_path = f"{working_dir}/config.json"
with open("config.json") as f:
    config_data = json.load(f)

# loading the GOOGLE_API_KEY
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]

# configuring google.generativeai with API key
genai.configure(api_key=GOOGLE_API_KEY)

# ---------- Load Gemini Chat Model ----------
def load_gemini_model():
    model = genai.GenerativeModel("gemini-2.5-flash")
    return model


# ---------- Image + Text Response ----------
def gemini_vision_response(prompt, image):
    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content([prompt, image])

    return response.text


# ---------- Embeddings ----------
def embeddings_model_response(input_text):
    embedding = genai.embed_content(
        model="gemini-embedding-001",
        content=input_text,
        task_type="retrieval_document"
    )

    return embedding["embedding"]


# ---------- Text Chat Response ----------
def gemini_text_response(user_prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(user_prompt)

    return response.text
# result = gemini_pro_response("What is Machine Learning")
# print(result)
# print("-"*50)
#
#
# image = Image.open("test_image.png")
# result = gemini_pro_vision_response("Write a short caption for this image", image)
# print(result)
# print("-"*50)
#
#
# result = embeddings_model_response("Machine Learning is a subset of Artificial Intelligence")
# print(result)