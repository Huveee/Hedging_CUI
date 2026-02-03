from pandas.core.ops.docstrings import key
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
    key="chatbot_confidence"
)

correctness = st.radio(
    "How likely is the chatbot to be correct?",
    options=list(range(1,11)),
    horizontal=True,
    index=None,
    key="chatbot_correctness"
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


if st.button("Done",key="done_button2"):
    missing = []

    # 1) Check if the confidence and correctness questions are answered
    conf = st.session_state.get("chatbot_confidence")
    corr = st.session_state.get("chatbot_correctness")

    if conf is None:
        missing.append("chatbot_confidence")
    else:
        participant.save_answer(user_id, "chatbot_confidence", conf, answers_key="answers_hct")

    if corr is None:
        missing.append("chatbot_correctness")
    else:
        participant.save_answer(user_id, "chatbot_correctness", corr, answers_key="answers_hct")

    # 2) Check if the HCT questions are answered
    for q in questions_hct:
        val = st.session_state.get(q["id"])
        if val is None:
            missing.append(q["id"])
        else:
            participant.save_answer(user_id, q["id"], val, answers_key="answers_hct")

    # 3) Eksik varsa uyar
    if missing:
        st.warning("Please answer all questions before proceeding.")
        # debug istersen:
        # st.write("Missing:", missing)
        st.stop()

    st.success("All answers recorded. Thank you!")
    st.switch_page("pages/4_Thanks.py")







