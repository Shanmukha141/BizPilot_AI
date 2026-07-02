from google.adk import Agent, Workflow
from app.config import settings
from app.tools.system_tools import get_current_datetime, basic_calculator
from app.tools.rag_tool import search_business_documents

# A clean, single agent for testing Phase 3 conversation memory
bizpilot_agent = Agent( 
    name="bizpilot_core_agent",
    model=settings.GEMINI_MODEL,
    instruction="""You are the BizPilot AI Core Assistant. 
    You are a professional business operations copilot. 
    Remember details the user tells you about their business and use them in conversation.""",
    # Add tools so the agent can answer questions about time and do calculations
    tools=[get_current_datetime, basic_calculator, search_business_documents]
)

core_workflow = Workflow(
    name="core_workflow",
    edges=[
        ("START", bizpilot_agent)
    ]
)