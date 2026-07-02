from flask import Flask, request, jsonify
from flask_cors import CORS
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agents.supervisor import core_workflow

app = Flask(__name__)
# Enable CORS so Streamlit can talk to Flask without origin issues
CORS(app) 

# Persistent session service to maintain conversation history
session_service = InMemorySessionService()

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.json
        user_message = data.get("message")
        history = data.get("history", []) # Catch the history from Streamlit

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Create the runner (we MUST include session_service as it's required by ADK)
        runner = Runner(
            node=core_workflow, 
            app_name="BizPilot",
            session_service=session_service,
            auto_create_session=True
        )
        
        # Format the history into a string so the AI has context
        final_prompt = user_message
        if len(history) > 1:
            context_string = "CONVERSATION HISTORY:\n"
            # Streamlit includes the current prompt in the history list, 
            # so we loop through everything EXCEPT the very last item
            for msg in history[:-1]:
                role = "User" if msg["role"] == "user" else "Assistant"
                context_string += f"{role}: {msg['content']}\n"
            
            context_string += f"\nCURRENT REQUEST: {user_message}"
            final_prompt = context_string

        # Build the message payload using google-genai types
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=final_prompt)]
        )
        
        # Execute the workflow
        events = runner.run(
            user_id="default_user",
            session_id="default-session",
            new_message=new_message
        )
        
        response_text = ""
        print("\n" + "="*50)
        print(f"PROMPT SENT TO MODEL:\n{final_prompt}")
        print("-" * 50)
        
        try:
            for event in events:
                # Safely check for and print tool calls based on the ADK Event structure
                if getattr(event, 'content', None) and getattr(event.content, 'parts', None):
                    for part in event.content.parts:
                        if getattr(part, 'function_call', None):
                            print(f"🛠️ TOOL CALL REQUESTED: [{part.function_call.name}]")
                        
                        if getattr(part, 'function_response', None):
                            print(f"✅ TOOL RESULT RECEIVED: [{part.function_response.name}]")
                            
                        # Extract the conversational text
                        if getattr(part, 'text', None):
                            response_text += part.text
        except Exception as e:
            error_msg = str(e)
            print(f"❌ ADK Exception Caught: {error_msg}")
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                response_text = "I'm sorry, but we are currently hitting the Gemini API rate limits (HTTP 429). Please wait about 1 minute and try again!"
            else:
                response_text = f"An unexpected error occurred during processing: {error_msg}"
                
        print("="*50 + "\n")
        
        if not response_text or not response_text.strip():
            response_text = "⚠️ The agent returned no text. This usually happens when you hit the Gemini Free Tier Rate Limit (HTTP 429). Please wait 1 minute and try again!"

        return jsonify({
            "status": "success",
            "response": response_text.strip()
        })

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)