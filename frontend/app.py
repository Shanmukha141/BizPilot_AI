import streamlit as st
import uuid
import pandas as pd
import os
import sys

# --- FIX FOR CIRCULAR IMPORT ---
# Remove 'frontend' from sys.path so that this app.py doesn't shadow the 'app' module in the backend
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

# Add 'backend' to sys.path so that Python can find the backend's 'app' package
BACKEND_DIR = os.path.abspath(os.path.join(script_dir, '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 1. IMPORT YOUR BACKEND LOGIC DIRECTLY
# Now we can import directly from 'app' since 'backend' is in our path!
from app.agents.supervisor import core_workflow
from app.tools.rag_tool import ingest_pdf, get_all_documents

# Ensure data dir exists (for uploads)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 2. INITIALIZE THE RUNNER ONCE
@st.cache_resource
def get_runner():
    # In monolith mode, Streamlit directly instantiates the ADK runner
    return Runner(
        node=core_workflow, 
        app_name="BizPilot_Monolith",
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

runner = get_runner()

# 3. CREATE THE LOCAL CHAT HANDLER
def handle_chat(user_message: str, session_id: str) -> str:
    """Runs the multi-agent ADK graph directly within Streamlit."""
    new_message = types.Content(role="user", parts=[types.Part(text=user_message)])
    events = runner.run(
        user_id="streamlit_user",
        session_id=session_id,
        new_message=new_message
    )
    
    response_text = ""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
    return response_text

st.set_page_config(page_title="BizPilot AI", page_icon="✨", layout="wide")

# --- Custom CSS for clean UI ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Only constrain width on chat page */
    .stChatFloatingInputContainer {
        padding-bottom: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize global session tracking
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am BizPilot AI. How can I assist you with your business operations today?"}]
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("✨ BizPilot AI Engine")
st.sidebar.caption("Autonomous Business Operations Copilot")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation", 
    ["💬 Main Assistant Chat", "📁 Uploaded Files", "📊 Business Analytics", "📋 Operations Reports", "🤖 Agent Status"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Upload")
st.sidebar.caption("Upload business documents (PDFs) to give the AI context.")

# File Uploader
uploaded_file = st.sidebar.file_uploader("Upload PDF Document", type=["pdf"], label_visibility="collapsed")

# Automatic Upload Logic (direct Python function calls now)
if uploaded_file is not None:
    if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
        with st.sidebar:
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                try:
                    # Save the uploaded file to backend/data
                    file_path = os.path.join(DATA_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Direct function call to ingest_pdf instead of requests.post
                    ingest_pdf(file_path)
                    
                    st.success(f"✅ {uploaded_file.name} added to Vector DB!")
                    st.session_state.last_uploaded = uploaded_file.name
                    if uploaded_file.name not in st.session_state.uploaded_docs:
                        st.session_state.uploaded_docs.append(uploaded_file.name)
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")
    else:
        st.sidebar.success(f"✅ {uploaded_file.name} is active.")

# --- PAGE 1: CHAT INTERFACE ---
if page == "💬 Main Assistant Chat":
    st.title("💬 BizPilot Operations Chat")
    
    # Optional button to clear chat
    if st.button("Clear Conversation"):
        st.session_state.messages = [{"role": "assistant", "content": "Conversation cleared. How can I help you?"}]
        st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input Loop
    if prompt := st.chat_input("Ask BizPilot to search documents, compile metrics, or analyze data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent routing & processing..."):
                try:
                    # Restore the manual conversation history injection from the old Flask app
                    final_prompt = prompt
                    history = st.session_state.messages
                    if len(history) > 1:
                        context_string = "CONVERSATION HISTORY:\n"
                        # Loop through everything EXCEPT the very last item (which is the current prompt)
                        for msg in history[:-1]:
                            role = "User" if msg["role"] == "user" else "Assistant"
                            context_string += f"{role}: {msg['content']}\n"
                        
                        context_string += f"\nCURRENT REQUEST: {prompt}"
                        final_prompt = context_string

                    # Append hint to prompt if documents are uploaded
                    enhanced_prompt = final_prompt
                    if st.session_state.uploaded_docs:
                        enhanced_prompt += f"\n\n[SYSTEM HINT: The user has uploaded these documents: {', '.join(st.session_state.uploaded_docs)}. If they are asking about them, please use the search_business_documents tool to search them.]"

                    # 4. SWAP FLASK REQUEST FOR DIRECT FUNCTION CALL
                    assistant_reply = handle_chat(enhanced_prompt, st.session_state.session_id)
                    
                    if not assistant_reply or not assistant_reply.strip():
                        assistant_reply = "⚠️ The agent returned no text. This might be due to an error or rate limiting."

                    st.markdown(assistant_reply)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                except Exception as e:
                    st.error(f"Agent Execution Error: {str(e)}")

# --- PAGE 2: UPLOADED FILES ---
elif page == "📁 Uploaded Files":
    st.title("📁 Document Knowledge Base")
    st.caption("Manage business files and SOPs ingested into ChromaDB vector storage.")
    
    st.markdown("### Currently Active Documents")
    
    try:
        with st.spinner("Fetching active documents..."):
            # Direct call to get_all_documents instead of requests.get
            docs = get_all_documents()
            if not docs:
                st.info("No documents uploaded yet. Use the Quick Upload in the sidebar.")
            else:
                for doc in docs:
                    st.success(f"📄 {doc} — *Status: Active in ChromaDB Index*")
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")

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