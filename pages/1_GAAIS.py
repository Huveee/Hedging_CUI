import streamlit as st

if not st.session_state.get("consent_ok"):
    st.switch_page("Consent.py")

st.title("QUESTIONNAIRE 1")


sentiment_mapping = ["strongly disagree", "somewhat disagree", "neutral", "somewhat agree", "strongly agree"]
selected = st.feedback("faces")
if selected is not None:
    st.markdown(f"You selected {sentiment_mapping[selected]}.")