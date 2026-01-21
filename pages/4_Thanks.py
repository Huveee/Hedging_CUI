import streamlit as st

consent_done = st.session_state.get("consent_ok")
gaais_done = st.session_state.get("gaais_ok")
chat_done = st.session_state.get("chat_ok")
questionnaire_done=st.session_state.get("questionnaire_ok")

if not consent_done or not gaais_done or not chat_done or not questionnaire_done:
    st.switch_page("pages/3_Questionnaire.py")


st.markdown("""
# Thank you!

#### Your responses have been recorded.

#### You may now close this tab.

""")



