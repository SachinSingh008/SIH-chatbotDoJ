from flask import Flask, request, jsonify, render_template
import re
import google.generativeai as genai

app = Flask(__name__)

# Configure the Gemini AI
genai.configure(api_key='AIzaSyAO36_LDr2H1jojusoSo72mscY6lA6BQO4')
model = genai.GenerativeModel('gemini-pro')

responses = {
  
}


def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I'm sorry, I couldn't get an answer from Gemini. Error: {str(e)}"

def get_response(user_input):
    user_input = user_input.lower()
    for pattern, response in responses.items():
        if re.search(pattern, user_input):
            return response
    
    # If no predefined response is found, use Gemini
    gemini_prompt = f"""As an AI assistant for the Department of Justice in India, 
    please provide a concise and accurate answer to the following question:
    {user_input}
    Focus on legal matters, court procedures, and DoJ services."""
    
    gemini_response = get_gemini_response(gemini_prompt)
    return f"I don't have a predefined answer for that, but here's what I found:\n{gemini_response}"

@app.route('/get_response', methods=['POST'])
def chatbot_response():
    user_input = request.json['message']
    response = get_response(user_input)
    return jsonify({'response': response})

@app.route('/chat_window')
def chat_window():
    return render_template('chat_window.html')

@app.route('/')
def home():
    return render_template('chat_window.html')

if __name__ == '__main__':
    app.run(debug=True)