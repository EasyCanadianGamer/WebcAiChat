# WebAIChat

## About
Learning about generative AI and by using Google Gemini API I can learn how to make your own characters for free. Similar to Character.AI but its unrestrcited
and free, well locally. All it can do its for know be a character. 


## How to run it locally:

### VSCode
First you need Python: The version I recommend is Python 3.10.


You need these dependencies:
```
pip install -q -U flask 
pip install -q -U google-generativeai 
```
or you can download the `requirement.txt` and do `pip install -q -U -r requirement.txt`

after you need import a couple items and your API:
Steps to access your Gemini API:
1. Go to you [Google AI Studio](https://aistudio.google.com/app)
2. Login into your google account
3. Create your [API Key](https://aistudio.google.com/app/apikey)
4. And copy it to where it says "YOUR_API_KEY_HERE"
```
import pathlib
import textwrap
import google.generativeai as genai


GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)
```

Then you can just run this for loop command to get all the models to use:
```
 for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
         print(model.name)
```

After choosing your model ( I chose "gemini-1.5-pro-latest" ) save it as a MODEL_NAME variable and everything else :
```
MODEL_NAME = "gemini-1.5-pro-latest"


instruction = ("You are a Assistant name Gemeni, you like to help other with anything")
model = genai.GenerativeModel(MODEL_NAME, system_instruction=instruction)

chat = model.start_chat()
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

    print("ChatBot: "+ response.text)
```

If you want to know more check the documentaion of [Gemini](https://ai.google.dev/docs) and their [cookbook](https://github.com/google-gemini/cookbook?tab=readme-ov-file)

## Google Colab: Coming Soon

