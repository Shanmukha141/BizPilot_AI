import json

# --- FINANCE TOOLS ---
def analyze_revenue(quarter: str) -> str:
    """Provides revenue analysis for a given quarter (e.g., 'Q1', 'Q2', 'Q3', 'Q4')."""
    # Mock database response(***we have to add data***)
    data = {
        "Q1": {"revenue": "$1.1M", "growth": "8%", "top_product": "Enterprise SaaS"},
        "Q2": {"revenue": "$1.2M", "growth": "12%", "top_product": "Cloud Hosting"},
        "Q3": {"revenue": "$1.5M", "growth": "15%", "top_product": "Consulting"},
        "Q4": {"revenue": "$1.8M", "growth": "20%", "top_product": "Enterprise SaaS"}
    }
    result = data.get(quarter.upper(), {"error": "Data not found for this quarter."})
    return json.dumps(result)

def analyze_expenses(department: str) -> str:
    """Provides expense analysis for a specific department (e.g., 'Marketing', 'Engineering', 'Sales')."""
    data = {
        "Marketing": "$120,000",
        "Engineering": "$450,000",
        "Sales": "$200,000"
    }
    result = data.get(department.capitalize(), "Department not found.")
    return f"Total expenses for {department.capitalize()}: {result}"

# --- SALES TOOLS ---
def get_sales_insights(region: str) -> str:
    """Retrieves sales reports and customer insights for a specific region (e.g., 'North America', 'Europe', 'Asia')."""
    insights = {
        "North America": "High enterprise adoption. 45 new accounts closed.",
        "Europe": "Steady growth in mid-market. GDPR compliance is a key selling point.",
        "Asia": "Rapid expansion in the tech sector. 60 new accounts closed."
    }
    result = insights.get(region.title(), "No insights available for this region.")
    return f"Sales Insights for {region.title()}: {result}"

# --- HR TOOLS ---
def summarize_resume(candidate_name: str, resume_text: str) -> str:
    """Summarizes a candidate's resume and highlights key strengths."""
    # In a real app, this might do an internal LLM call or parse a PDF.
    # For the tool layer, we instruct the agent to use this to structure the output.
    return f"Candidate {candidate_name} summary: Strong background in backend development and API design based on provided text."

# --- EMAIL TOOL ---
def draft_email(recipient: str, subject: str, core_message: str) -> str:
    """Drafts a professional email."""
    # This simulates pushing to a Gmail API or SMTP server
    email_format = f"""
    To: {recipient}
    Subject: {subject}
    
    {core_message}
    
    Best regards,
    BizPilot AI
    """
    return f"Email successfully drafted:\n{email_format}"

# --- CALENDAR TOOL ---
def schedule_meeting(attendees: str, time: str, topic: str) -> str:
    """Schedules a meeting on the calendar."""
    # Simulates a Google Calendar API call
    return f"Meeting successfully scheduled for {time} regarding '{topic}'. Invites sent to: {attendees}."