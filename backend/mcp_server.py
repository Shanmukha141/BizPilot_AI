# backend/mcp_server.py
from mcp.server.fastmcp import FastMCP
import json

# Initialize the MCP Server
mcp = FastMCP("BizPilot_Enterprise_Server")

# --- FINANCE TOOLS ---
@mcp.tool()
def analyze_revenue(quarter: str) -> str:
    """Provides revenue analysis for a given quarter (e.g., 'Q1', 'Q2', 'Q3', 'Q4')."""
    data = {
        "Q1": {"revenue": "$1.1M", "growth": "8%", "top_product": "Enterprise SaaS"},
        "Q2": {"revenue": "$1.2M", "growth": "12%", "top_product": "Cloud Hosting"},
        "Q3": {"revenue": "$1.5M", "growth": "15%", "top_product": "Consulting"},
        "Q4": {"revenue": "$1.8M", "growth": "20%", "top_product": "Enterprise SaaS"}
    }
    result = data.get(quarter.upper(), {"error": "Data not found for this quarter."})
    return json.dumps(result)

@mcp.tool()
def analyze_expenses(department: str) -> str:
    """Provides expense analysis for a specific department (e.g., 'Marketing', 'Engineering', 'Sales')."""
    data = {
        "Marketing": "$120,000",
        "Engineering": "$450,000",
        "Sales": "$200,000"
    }
    result = data.get(department.capitalize(), "Department not found.")
    return f"Total expenses for {department.capitalize()}: {result}"

# --- CALENDAR TOOL ---
@mcp.tool()
def schedule_meeting(attendees: str, time: str, topic: str) -> str:
    """Schedules a meeting on the corporate calendar."""
    return f"Meeting successfully scheduled for {time} regarding '{topic}'. Invites sent to: {attendees}."

if __name__ == "__main__":
    # This runs the server using standard stdio communication (required for MCP)
    mcp.run()