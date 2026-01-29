import streamlit as st
from data.questions_hct import questions_hct
import utils.sidebar as sidebar
import utils.participant as participant

sidebar.hide_sidebar()


st.title("Questionnaire") #title of the page

confidence = st.radio(
    "How confident did the chatbot seem?",
    options=list(range(1,11)),
    horizontal=True,
    index=None,
    key="q_confidence"
)

correctness = st.radio(
    "How likely is the chatbot to be correct?",
    options=list(range(1,11)),
    horizontal=True,
    index=None,
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

user_id = st.session_state["user_id"]

if st.button("Done"):
    missing_answers=False
    answers = participant.load_answers(user_id,answers_key="answers_hct")  # Load the answers from the file
    for answer in answers.values():
        if answer is None:
            missing_answers=True
            break
    if missing_answers:
        st.warning("Please answer all questions before proceeding.")
    else:
        st.success("All answers recorded. Thank you!")
        st.switch_page("pages/4_Thanks.py")






