import streamlit as st
import requests
import uuid
import pandas as pd

# Configuration
FLASK_BACKEND_URL = "http://127.0.0.1:5000/api/chat"

st.set_page_config(page_title="BizPilot AI - Dashboard", page_icon="👔", layout="wide")

# 1. Sidebar Navigation
st.sidebar.title("BizPilot AI Engine")
st.sidebar.caption("Autonomous Business Operations Copilot")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation", 
    ["💬 Main Assistant Chat", "📁 Uploaded Files", "📊 Business Analytics", "📋 Operations Reports", "🤖 Agent Status"]
)

# Initialize global session tracking for memory
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = ["sample_policy.pdf"] # Pre-populated with your Phase 5 file

# --- PAGE 1: CHAT INTERFACE ---
if page == "💬 Main Assistant Chat":
    st.title("💬 BizPilot Operations Chat")
    st.caption("Ask questions about math, dates, or search internal company records.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input Loop
    if prompt := st.chat_input("Ask BizPilot to calculate something, search files, or compile metrics..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent routing & processing..."):
                try:
                    payload = {
                        "message": prompt,
                        "session_id": st.session_state.session_id,
                        "history": st.session_state.messages
                    }
                    response = requests.post(FLASK_BACKEND_URL, json=payload)
                    response_data = response.json()

                    if response.status_code == 200:
                        assistant_reply = response_data["response"]
                        st.markdown(assistant_reply)
                        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                    else:
                        st.error(f"Error: {response_data.get('error', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error: Is your Flask server running on port 5000?")

# --- PAGE 2: UPLOADED FILES ---
elif page == "📁 Uploaded Files":
    st.title("📁 Document Knowledge Base")
    st.caption("Manage business files and SOPs ingested into ChromaDB vector storage.")
    
    uploaded_file = st.file_uploader("Ingest new business PDF document", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Process & Embed Document"):
            with st.spinner("Parsing text and calculating chunk embeddings..."):
                # In Phase 12 we will wire this to a Flask '/api/upload' route.
                # For now, append to local memory state to simulate system tracking.
                if uploaded_file.name not in st.session_state.uploaded_docs:
                    st.session_state.uploaded_docs.append(uploaded_file.name)
                st.success(f"Successfully chunked and saved '{uploaded_file.name}' into vector database.")
                
    st.markdown("### Currently Active Documents")
    for doc in st.session_state.uploaded_docs:
        st.info(f"📄 {doc} — *Status: Active in ChromaDB Index*")

# --- PAGE 3: BUSINESS ANALYTICS ---
elif page == "📊 Business Analytics":
    st.title("📊 Operational & Financial Analytics")
    st.caption("Real-time view of pipeline data pulled by the SQL agent infrastructure.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Q3 Target Revenue", value="$1.2M", delta="12% vs Last Quarter")
    col2.metric(label="Active Operating Expenses", value="$420,000", delta="-4% Optimization")
    col3.metric(label="HR Hiring Pipeline Openings", value="14 Positions", delta="2 Filled this week")
    
    st.markdown("### Revenue Breakdown Trend")
    chart_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Sales Revenue": [120000, 150000, 140000, 180000, 210000, 250000],
        "Operating Costs": [90000, 95000, 93000, 110000, 105000, 115000]
    })
    st.line_chart(chart_data.set_index("Month"))

# --- PAGE 4: OPERATIONS REPORTS ---
elif page == "📋 Operations Reports":
    st.title("📋 Automated Management Reports")
    st.caption("Generate or download recent summaries prepared by the Report agent tool layer.")
    
    st.markdown("### Available Operational Summaries")
    reports_df = pd.DataFrame({
        "Report Name": ["Q2 Financial Balance Sheet.pdf", "Employee Policy Compliance Audit.pdf", "CRM Pipeline Follow-up Logs.csv"],
        "Generated By": ["Finance Agent", "HR Agent", "Sales Agent"],
        "Timestamp": ["2026-07-01 10:30", "2026-06-28 14:15", "2026-07-03 09:00"]
    })
    st.table(reports_df)
    st.button("Trigger Full System Sync Report Summary")

# --- PAGE 5: AGENT STATUS ---
elif page == "🤖 Agent Status":
    st.title("🤖 Multi-Agent Orchestration Logs")
    st.caption("Monitor the heartbeats, skill profiles, and operational parameters of your active ADK network.")
    
    agents_grid = [
        {"Agent": "Supervisor Agent", "Type": "Root Router", "Status": "🟢 Idle / Listening", "Model": "gemini-2.5-flash"},
        {"Agent": "Finance Agent", "Type": "SQL Database Worker", "Status": "🟢 Connected", "Model": "gemini-2.5-flash"},
        {"Agent": "Document Agent", "Type": "ChromaDB RAG Worker", "Status": "🟢 Connected", "Model": "gemini-2.5-flash"},
        {"Agent": "Email Agent", "Type": "Communications Protocol", "Status": "🟡 Sleeping", "Model": "gemini-2.5-flash"}
    ]
    st.json(agents_grid)