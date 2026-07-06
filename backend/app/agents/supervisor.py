from google.adk import Agent, Workflow
from app.config import settings
from app.tools.system_tools import get_current_datetime, basic_calculator

# Import all the specialized workers
from app.agents.workers import finance_agent, document_agent, sales_agent, admin_agent

# The Supervisor acts as the Phase 8 Planner
supervisor_agent = Agent(
    name="supervisor_agent",
    model=settings.GEMINI_MODEL,
    instruction="""You are the BizPilot AI CEO and Supervisor. 
    You manage a team of specialized agents: finance_agent, document_agent, sales_agent, and admin_agent.
    Analyze the user's request and delegate the task to the most appropriate agent.
    You can handle basic math and date/time questions yourself.""",
    tools=[get_current_datetime, basic_calculator],
    sub_agents=[finance_agent, document_agent, sales_agent, admin_agent]
)

# The Phase 9 Multi-Agent Routing Graph
core_workflow = Workflow(
    name="core_workflow",
    edges=[
        ("START", supervisor_agent)
    ]
)