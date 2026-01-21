import streamlit as st
from data.questions_hct import questions_hct

consent_done = st.session_state.get("consent_ok")
gaais_done = st.session_state.get("gaais_ok")
chat_done = st.session_state.get("chat_ok")

if not consent_done or not gaais_done or not chat_done:
    st.switch_page("pages/2_Chat.py")

st.title("Questionnaire") #title of the page


confidence = st.slider(
    "How confident did the chatbot seem?",
    min_value=1,
    max_value=10,
    key="q_confidence"
)

correctness = st.slider(
    "How likely is the chatbot to be correct?",
    min_value=1,
    max_value=10,
    key="q_correctness"
)

for question in questions_hct:
    st.radio(
        question["text"], #show the question text,
        options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
        key=question["id"],
        index=None,
    )
    st.divider() #To add line between questions


if st.button("Done"):
    missing_answers=False
    for question in questions_hct:
        if st.session_state.get(question["id"]) is None:
            missing_answers=True
            break
    if missing_answers:
        st.warning("Please answer all questions before proceeding.")
    else:
        st.success("All answers recorded. Thank you!")
        st.session_state["questionnaire_ok"] = True
        st.switch_page("pages/4_Thanks.py")






