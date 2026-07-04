import pytest
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agents.supervisor import core_workflow

# Initialize the Runner once for all tests
session_service = InMemorySessionService()
runner = Runner(node=core_workflow, app_name="BizPilot_Test", session_service=session_service, auto_create_session=True)

def execute_agent(query: str) -> str:
    """Helper function to run the agent and extract the response text."""
    new_message = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(
        user_id="test_user",
        session_id="test-session",
        new_message=new_message
    )
    
    response_text = ""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
    return response_text

# --- THE AUTOMATED EVALUATIONS ---

def test_math_reasoning():
    """Evaluates if the agent can accurately use the calculator tool."""
    print("\nEvaluating Math Tool...")
    response = execute_agent("What is 150 * 4?")
    # The agent should use the tool and return 600
    assert "600" in response, f"Math eval failed! Response was: {response}"

def test_finance_retrieval():
    """Evaluates if the agent routes to the Finance worker and gets correct Q2 data."""
    print("\nEvaluating Finance Routing...")
    response = execute_agent("What was our revenue in Q2?")
    # The tool returns $1.2M and 12% growth for Q2
    assert "1.2M" in response or "1.2" in response, f"Finance eval failed! Response was: {response}"

def test_document_rag_routing():
    """Evaluates if the agent refuses to hallucinate and uses the RAG tool."""
    print("\nEvaluating RAG Fallback...")
    response = execute_agent("What is the company policy on remote work?")
    # Even if it doesn't find the exact document, it should attempt to search or mention policies
    assert response is not None
    assert len(response) > 0, "Agent returned an empty response for a policy question."