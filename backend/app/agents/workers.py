# Specialized worker definitions
from google.adk import Agent
from app.config import settings

# Import the specialized tools
from app.tools.rag_tool import search_business_documents 
from app.tools.business_tools import (
    analyze_revenue, analyze_expenses, get_sales_insights, 
    summarize_resume, draft_email, schedule_meeting
)

# 1. Finance Agent
finance_agent = Agent(
    name="finance_agent",
    model=settings.GEMINI_MODEL,
    instruction="You are the Finance Agent. You analyze revenue and expenses. Provide clear, formatted financial summaries.",
    tools=[analyze_revenue, analyze_expenses]
)

# 2. Document & HR Agent
document_agent = Agent(
    name="document_agent",
    model=settings.GEMINI_MODEL,
    instruction="You are the Document and HR Agent. You search the vector database for any uploaded business documents, contracts, SOPs, and general files to answer user queries. You also handle employee policies and recruitment summaries.",
    tools=[search_business_documents, summarize_resume]
)

# 3. Sales & SQL Agent
sales_agent = Agent(
    name="sales_agent",
    model=settings.GEMINI_MODEL,
    instruction="You are the Sales Agent. You query regional sales insights and summarize customer data.",
    tools=[get_sales_insights]
)

# 4. Communications Agent (Email & Calendar)
admin_agent = Agent(
    name="admin_agent",
    model=settings.GEMINI_MODEL,
    instruction="You are the Administrative Agent. You draft emails and schedule calendar meetings.",
    tools=[draft_email, schedule_meeting]
)