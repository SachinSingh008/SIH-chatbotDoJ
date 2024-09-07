from flask import Flask, request, jsonify, render_template
import re
import google.generativeai as genai
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure the Gemini AI
genai.configure(api_key='AIzaSyAO36_LDr2H1jojusoSo72mscY6lA6BQO4')
model = genai.GenerativeModel('gemini-pro')

responses = {
    
    r"divisions of doj|doj divisions": """The Department of Justice (DoJ) has several key divisions:

1. Legal Affairs Division
2. Judicial Appointments Division
3. Access to Justice Division
4. Infrastructure Development for Judiciary Division
5. Special Courts Division
6. eCourts Project Division
7. Legal Aid Division
8. Training and Education Division""",

    r"judges|vacancies|appointments": """Current information on judges (as of April 2024):

1. **Supreme Court:** 34 judges including the Chief Justice of India
2. **High Courts:** 25 High Courts with a total sanctioned strength of 1,114 judges
3. **District & Subordinate Courts:** Approximately 24,000 judges

*Please note that the exact number of vacancies can change frequently. For the most up-to-date information, visit the official Department of Justice website.*""",

    r"pendency of cases|njdg": """To check the pendency of cases through National Judicial Data Grid (NJDG):

1. Visit the NJDG website (https://njdg.ecourts.gov.in/)
2. Select the desired court type
3. View the dashboard for case pendency statistics
4. Use filters to narrow down the data""",

    r"traffic violation fine|pay fine": """To pay a traffic violation fine:

1. Visit your state's e-challan payment portal
2. Enter your challan number or vehicle details
3. Review the violation details and fine amount
4. Choose a payment method and complete the payment
5. Save the receipt""",

    r"live streaming|court cases": """For live streaming of court cases:

1. Check the official website of the Supreme Court or respective High Courts
2. Look for a 'Live Streaming' or 'YouTube' link
3. Some courts have dedicated YouTube channels for live streaming
4. Not all cases are live-streamed; it depends on the court's discretion""",

    r"efiling|epay": """Steps for eFiling and ePay:

1. Visit the eFiling portal (https://efiling.ecourts.gov.in/)
2. Register or log in to your account
3. Choose 'New Case' or 'Documents in Existing Case'
4. Fill in the required details and upload necessary documents
5. Pay the court fees online using the ePay feature
6. Submit the filing and note the confirmation number""",

    r"fast track courts": """About Fast Track Courts:

1. **Purpose:** To expedite trials for certain types of cases
2. **Focus:** Cases like sexual offenses, crimes against children, and senior citizens
3. **Goal:** Complete trials within 6 months to 2 years
4. **Operation:** Simplified procedures to reduce delays
5. **Staffing:** Experienced judges and support personnel""",

    r"ecourts app|mobile app": """To download the eCourts Services Mobile app:

1. Open Google Play Store (Android) or App Store (iOS)
2. Search for 'eCourts Services'
3. Look for the app developed by eCommittee, Supreme Court of India
4. Click 'Install' or 'Get' to download the app
5. Open the app and register to access various e-court services""",

    r"tele law|legal services": """Availing Tele Law Services:

1. Visit your nearest Common Service Centre (CSC)
2. Request a Tele Law consultation
3. Connect with a panel lawyer via video conference
4. Discuss your legal issue and receive advice
5. Schedule follow-up consultations if needed
6. The service is free for eligible beneficiaries""",

    r"case status": """To know the current status of a case:

1. Visit the eCourts website (https://ecourts.gov.in/ecourts_home/)
2. Click on 'Case Status'
3. Choose the court type (Supreme Court, High Court, or District Court)
4. Enter the required details (case number, filing number, or party name)
5. Click 'Go' to view the current status and history of the case"""
}

def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error in get_gemini_response: {str(e)}")
        return None

@app.route('/get_response', methods=['POST'])
def chatbot_response():
    try:
        user_input = request.json['message']
        is_first_message = request.json.get('is_first_message', False)
        logging.info(f"Received user input: {user_input}")
        
        response = get_response(user_input, is_first_message)
        
        if response is None:
            return jsonify({'error': 'Failed to generate response'}), 500
        
        logging.info(f"Sending response: {response}")
        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Error in chatbot_response: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def get_response(user_input, is_first_message):
    user_input = user_input.lower()
    
    # Check if it's the first message
    if is_first_message:
        return "Hi, I am Vaani. How may I help you?"
    
    # Check predefined responses
    for pattern, response in responses.items():
        if re.search(pattern, user_input):
            return response
    
    # If no predefined response, use Gemini
    gemini_prompt = f"""As Vaani, an AI assistant for the Department of Justice in India, provide a response to this query:
    {user_input}
    
    Structure your response as follows:
    1. A brief, direct answer (1-2 sentences).
    2. If the topic requires more explanation, add "Here are some key points:" followed by 3-5 concise bullet points.
    
    Focus only on legal matters, court procedures, and DoJ services directly related to the question. 
    Use **bold** for key terms."""
    
    gemini_response = get_gemini_response(gemini_prompt)
    return gemini_response if gemini_response else "I'm sorry, I couldn't generate a response at the moment. Please try again."


@app.route('/get_details', methods=['POST'])
def get_details():
    message = request.json['message']
    gemini_prompt = f"""As Vaani, an AI assistant for the Department of Justice in India, provide more detailed information about this topic:
    {message}
    Focus on legal matters, court procedures, and DoJ services directly related to the topic. 
    Keep the response concise. Use **bold** for key terms."""
    
    gemini_response = get_gemini_response(gemini_prompt)
    return jsonify({'response': gemini_response})

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

