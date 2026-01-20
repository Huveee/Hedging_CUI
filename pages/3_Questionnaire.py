import streamlit as st

consent_done = st.session_state.get("consent_ok")
gaais_done = st.session_state.get("gaais_ok")
chat_done = st.session_state.get("chat_ok")

if not consent_done or not gaais_done or not chat_done:
    st.switch_page("pages/2_Chat.py")