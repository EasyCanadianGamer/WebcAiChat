import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown




GOOGLE_API_KEY = "AIzaSyCshLoylaBl1E7CsF86vytLVpr4Nx2HxZw"
genai.configure(api_key=GOOGLE_API_KEY)


# for model in genai.list_models():
#     if 'generateContent' in model.supported_generation_methods:
#         print(model.name)


MODEL_NAME = "gemini-1.5-pro-latest"


instruction = ("You are a Assistant name Gemeni, you like to help other with anything")
model = genai.GenerativeModel(MODEL_NAME, system_instruction=instruction)

chat = model.start_chat()


# prompt = input()

# response = model.generate_content(
#     prompt,
#     safety_settings={
#         'HATE': 'BLOCK_NONE',
#         'HARASSMENT': 'BLOCK_NONE',
#         'SEXUAL' : 'BLOCK_NONE',
#         'DANGEROUS' : 'BLOCK_NONE'
#     })
# bool(response.prompt_feedback.block_reason)
# len(response.candidates)

# print(response.text)


while True:
    prompt = input("You:")
    response = model.generate_content(
        prompt,
        safety_settings={
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL' : 'BLOCK_NONE',
            'DANGEROUS' : 'BLOCK_NONE'
        })


    print("Shazia: "+ response.text)


    


