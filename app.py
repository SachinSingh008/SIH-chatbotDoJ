from flask import Flask, render_template, request, jsonify
import re
import google.generativeai as genai

app = Flask(__name__)

# Configure the Gemini AI
genai.configure(api_key='AIzaSyAO36_LDr2H1jojusoSo72mscY6lA6BQO4')
model = genai.GenerativeModel('gemini-pro')

responses = {
    r"hi|hello":"Hello! How can I help you today?",
    r"how are you":"I'm doing well, thank you! How about you?",
    r"what is your name":"I am the official bot for the Department of Justice, India. How can I assist you?",
    r"what does the department of justice do":"Hello! How can I help you today?",
    r"division|department": """The Department of Justice (DoJ) has several key divisions and functions:
1. Legal Affairs: Handles legal matters for the government.
2. Judicial Appointments: Manages the process of appointing judges to various courts.
3. Access to Justice: Works on improving access to legal services for all citizens.
4. Infrastructure Development for Judiciary: Oversees the development of court infrastructure.
5. Special Courts: Sets up Fast Track Special Courts for cases related to rape and POCSO Act.
6. eCourts Project: Implements computerization of courts across the country.
7. Legal Aid: Provides legal assistance to the poor and underprivileged.
8. Training: Offers financial assistance to the National Judicial Academy for training Judicial Officers.""",

    r"judge|supreme court|high court|district court": """Current information on judges and vacancies:
1. Supreme Court: Maximum strength of 34 judges, including the Chief Justice of India.
2. High Courts: There are 25 High Courts in India. The number of judges varies for each High Court.
3. District & Subordinate Courts: These courts form the backbone of the Indian judiciary at the local level.

For the most up-to-date information on current appointments and vacancies, please visit the official website of the Department of Justice or the respective court websites.""",

    r"pendency|case|njdg": """You can check the pendency of cases through the National Judicial Data Grid (NJDG):
1. Visit https://njdg.ecourts.gov.in/
2. The NJDG provides real-time data on pending cases across various courts in India.
3. You can view statistics by state, district, or court type.
4. The data includes information on case types, age of pending cases, and disposal rates.
5. This tool is part of the eCourts project to improve transparency and efficiency in the judicial system.""",

    r"traffic|fine|violation|pay": """To pay traffic violation fines:
1. Visit the e-Challan system at https://echallan.parivahan.gov.in/
2. Enter your vehicle number or challan number to find your pending challans.
3. Select the challan you want to pay and choose your preferred payment method.
4. Complete the payment process and keep the receipt for your records.
5. You can also pay fines through various mobile apps or at designated traffic police offices.""",

    r"live stream|streaming": """Live streaming of court cases:
1. The Supreme Court has begun live streaming of Constitution Bench cases.
2. You can watch these on the official YouTube channel of the Supreme Court.
3. This initiative aims to increase transparency and public access to important court proceedings.
4. Not all cases are live-streamed; the court decides which cases to broadcast.
5. Some High Courts have also started live streaming selected cases.""",

    r"efiling|file|epay": """Steps for eFiling and ePay:
1. Visit https://efiling.ecourts.gov.in/
2. Register as a user if you haven't already.
3. Log in and select 'New Case Filing' or 'Documents Filing' as per your requirement.
4. Fill in the required details and upload necessary documents.
5. Pay the court fees online using the ePay system.
6. Submit your filing and note down the CNR (Case Number Record) for future reference.
7. You can track the status of your case using this CNR number.""",

    r"fast track|special court": """Information on Fast Track Courts:
1. Fast Track Courts are special courts set up for speedy trial and disposal of cases.
2. They focus particularly on cases involving rape and offenses under the POCSO Act.
3. These courts aim to reduce the backlog of cases and provide swift justice.
4. They follow a streamlined process to expedite case hearings and judgments.
5. The establishment of these courts is part of the government's effort to address serious crimes efficiently.""",

    r"app|mobile|ecourt services": """Downloading and using the eCourts Services Mobile app:
1. Available on Google Play Store (Android) and App Store (iOS).
2. The app provides easy access to case status, court orders, and cause lists.
3. Features include case status tracking, checking daily case lists, and viewing court orders.
4. You can search cases using CNR number, case number, party name, or FIR number.
5. The app also provides information about court complexes and judges.""",

    r"tele law": """Availing Tele Law Services:
1. Tele Law provides legal advice to people in rural areas through video conferencing.
2. Services are available at Common Service Centers (CSCs) in rural areas.
3. To use the service, visit your nearest CSC and request a Tele Law consultation.
4. You'll be connected with a panel lawyer who will provide legal advice.
5. This service aims to bridge the gap in access to justice for rural and remote areas.
6. It covers various areas of law including family matters, property disputes, and criminal cases.""",

    r"status|current status": """Checking the current status of a case:
1. Visit the eCourts website: https://ecourts.gov.in/ecourts_home/
2. Click on 'Case Status' in the main menu.
3. You can search by CNR number, case number, party name, or FIR number.
4. Select the appropriate court (Supreme Court, High Court, or District Court).
5. Enter the required details and submit your query.
6. The system will display the current status, next hearing date, and other relevant information about your case."""
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

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)