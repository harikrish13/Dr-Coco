from flask import Flask, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from vector_database import vector_store
from flask_cors import CORS  # Import Flask-CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# OpenAI API client
#openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key="")

# OpenAI Assistant Configuration
assistant = client.beta.assistants.create(
    name="Dr. Coco",
    instructions="""
    You are a medical support assistant tasked with answering user questions or troubleshooting issues using a vector database of FAQs and customer support content.

### Knowledge Source:
- **Vector Database**: A searchable repository of FAQs and customer support information.

### Response Guidelines:
1. **Answer the User's Query**:
    - Provide clear, concise, and accurate answers or suggest appropriate solutions.
    - Use polite and empathetic language to ensure a helpful response.
    - Let the answers be clear and in bullet points if necessary. Break the answers into paragraphs and line spaces for clearer understanding
    - Do not include annotations of the sources


2. **Handle Unmatched Queries**:
    - If the query doesn’t match any information in the vector database:
        - Suggest contacting support at `support@dancervibe.com`.
        - Provide generic or contextually relevant suggestions, if possible.

### Response Format:
Your output must be in JSON format as follows:

{
    "message reply": "Your direct answer to the user’s query in short points.",
    "q_flag": 1
}

### Note:
    - "message reply" should be in HTML
    """,
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    model="gpt-4o-mini",
)

# Static suggestive questions and their responses
'''STATIC_SUGGESTIONS = {
    "What are the pricing plans?": '<p>🎉 Unlock all features for just <strong>$19.95/month</strong> after your free trial! 👉 Check out our <a href="https://dancervibe.com/pricing" target="_blank">Pricing Page</a> for details. 💃🕺</p>',
    "What features does the platform offer?": "<p><strong>Dancervibes</strong> offers tools for easy scheduling of classes and events, allowing you to manage bookings effectively.</p>\n<ul>\n    <li><strong>Payment Processing:</strong> Provides secure online payments and invoicing features.</li>\n    <li><strong>Studio Management Features:</strong> Helps with participant registrations, attendance tracking, and staff management.</li>\n</ul>\n<p>These features are designed to streamline operations and make studio management more efficient.</p>",
    "How can I sign up for a Dancervibes account?": 'To sign up <p>visit <a href="https://dancervibes.com" target="_blank">DancerVibes</a>, click on <strong>"Start your Free Trial"</strong>, fill in your dance studio details, and follow the prompts to complete your registration.</p>'
}'''

# Moderation function to check for inappropriate content
'''def check_moderation(input_message):
    moderation = client.moderations.create(input=input_message)
    flagged = moderation.results[0].flagged
    categories = moderation.results[0].categories
    return flagged, categories'''

# Helper function to fetch follow-up suggestions based on intent
'''def get_dynamic_suggestions(intent):
    suggestions_by_intent = {
        "Pricing": [
            "What is the cancellation policy?",
            "Are there any hidden fees?",
            "Do you offer discounts?"
        ],
        "Features": [
            "Can I track attendance and progress?",
            "Does the platform support multiple users?",
            "Are the features customizable?"
        ],
        "Technical": [
            "What is the uptime guarantee?",
            "How do I integrate with other tools?",
            "Is there API documentation?"
        ]
    }
    return suggestions_by_intent.get(intent, [])'''

# Process user message
def process_message(user_message):
    # Check for inappropriate content
    '''flagged, categories = check_moderation(user_message)
    if flagged:
        return {
            "message reply": '<p>Apologies, your message seems to contain inappropriate information. Please contact customer support at <a href="mailto:support@dancervibe.com">support@dancervibe.com</a>.</p>',
            "suggestions": [],
            "q_flag": None
        }'''

    # Greet and provide static suggestions
    if user_message.lower() in ["hi", "hello", "hey"]:
        return {
            "message reply": "Hello! I'm Dr. COCO - Your Pediatric Psychological Assistant. What can I help you with today?",
            "q_flag": None
        }

    # Check if message matches a static question
    '''if user_message in STATIC_SUGGESTIONS:
        return {
            "message reply": STATIC_SUGGESTIONS[user_message],
            "suggestions": [],
            "q_flag": None
        }'''

    # Query OpenAI assistant for dynamic answers
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"{user_message}",
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    if run.status == "completed":
        final_messages = list(client.beta.threads.messages.list(thread_id=thread.id))
        if not final_messages or not final_messages[0].content or not final_messages[0].content[0].text.value.strip():
            return {
                "message reply": "No response received from the assistant.",
                "q_flag": 0
            }

        # Extract response data from the assistant
        response_data = final_messages[0].content[0].text.value.strip()

        # Debug: Print the raw response data
        print("Raw Response Data:", response_data)

        try:
            # Directly parse the response if it's already a JSON object
            if isinstance(response_data, dict):
                response_json = response_data
            else:
                response_json = json.loads(response_data)

            response_message = response_json.get("message reply", "No reply available.")
            q_flag = response_json.get("q_flag", 0)

            return {
                "message reply": response_message,
                "q_flag": q_flag
            }
        except (json.JSONDecodeError, TypeError) as e:
            print(f"JSONDecodeError or TypeError: {e}")
            print("Raw Response Data:", response_data)
            return {
                "message reply": "Sorry, there was an error processing the response from the assistant.",
                "q_flag": 0
            }

    return {
        "message reply": "Sorry, I'm unable to process your request right now. Please try again later.",

        "q_flag": 0
    }



# Flask route for chatbot
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    response = process_message(user_message)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
