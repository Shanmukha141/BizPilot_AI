# BizPilot AI Project

This project implements the BizPilot AI application with a Flask backend and a Streamlit frontend.

## Architecture

- **backend/**: Contains the Flask application, settings, core tools, and worker/supervisor agents.
- **frontend/**: Contains the Streamlit user interface.

## Getting Started

### Prerequisites

- Python 3.10+
- Pip

### Setup Backend

1. Navigate to the `backend/` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your API keys in the `.env` file.
4. Run the Flask server:
   ```bash
   python -m app.main
   ```

### Setup Frontend

1. Navigate to the `frontend/` directory.
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
