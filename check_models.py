import google.generativeai as genai

# 🔑 Replace with your API key
API_KEY = "AIzaSyA96tANvRu6RXDXzYSDumxN1gl62SbJUwM"

genai.configure(api_key=API_KEY)

print("Available Models:\n")

for model in genai.list_models():
    print("Model Name:", model.name)
    print("Supported Methods:", model.supported_generation_methods)
    print("-" * 50)