import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown
from flask import Flask, request, render_template, redirect, url_for

GOOGLE_API_KEY = "AIzaSyCshLoylaBl1E7CsF86vytLVpr4Nx2HxZw"
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-1.5-pro-latest"

app = Flask(__name__)

model = None
@app.route('/', methods=['GET'])

@app.route('/prompt', methods=['GET', 'POST'])
def prompt():
    global model
    if request.method == 'POST':
        prompt = request.form['prompt']
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=prompt)
        return redirect(url_for('chatbot'))
    return render_template('prompt.html')

@app.route('/chat', methods=['GET', 'POST'])
def chatbot():
    global model
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = model.generate_content(
            user_input,
            safety_settings={
                'HATE': 'BLOCK_NONE',
                'HARASSMENT': 'BLOCK_NONE',
                'SEXUAL': 'BLOCK_NONE',
                'DANGEROUS': 'BLOCK_NONE'
            })
        return render_template('chat.html', user_text=user_input, ai_text=response.text)
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)