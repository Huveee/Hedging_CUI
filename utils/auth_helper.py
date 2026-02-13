import streamlit as st
import time

def require_user_id() -> str:
    """
    Ensures that a valid user_id is present in the session state.
    If not, it displays a warning and switches to the Consent page.
    Returns the user_id if valid.
    """
    user_id = st.session_state.get("user_id")
    
    if not user_id:
        st.warning("Redirecting to consent page...")
        time.sleep(1) # Give the user a moment to see the message
        st.switch_page("Consent.py")
        st.stop()
        
    return user_id
