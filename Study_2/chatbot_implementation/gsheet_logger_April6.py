# gsheet_logger.py
import streamlit as st
import gspread
from datetime import datetime
import time

HEADERS = ["session_id", "prolific_pid", "prolific_study_id", "prolific_session_id", "timestamp", "user_message", "bot_message", "condition"]

def get_client():
    """Return a gspread client using service account."""
    if "gsheet_gc" in st.session_state:
        return st.session_state["gsheet_gc"]

    # Use Streamlit secrets (Streamlit Cloud)
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
   

    st.session_state["gsheet_gc"] = gc
    return gc

def get_worksheet(sheet_url):
    """Return the first worksheet, create headers if missing."""
    gc = get_client()
    try:
        sh = gc.open_by_url(sheet_url)
        ws = sh.sheet1
        if not ws.row_values(1):
            ws.append_row(HEADERS, value_input_option="USER_ENTERED")
        return ws
    except Exception:
        return None
    
def log_exchange(sheet_url, session_id, user_message, bot_message, condition=""):
    """Append one row: user + bot messages in the same row."""
    ws = get_worksheet(sheet_url)
    if ws is None:
      return False  # gracefully fail if worksheet not available
    
    timestamp = datetime.utcnow().isoformat()
    row = [ 
        session_id,
        st.session_state.get("prolific_pid", ""),
        st.session_state.get("prolific_study_id", ""),
        st.session_state.get("prolific_session_id", ""),
        timestamp,
        user_message,
        bot_message,
        condition
    ]

    retries = 3
    for i in range(retries):
        try:
            ws.append_row(row, value_input_option="USER_ENTERED")
            return True
        except Exception:
            time.sleep(0.3*(i+1))
    return False