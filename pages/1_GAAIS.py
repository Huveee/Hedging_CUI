from pandas.core.ops.docstrings import key
import streamlit as st
from data.questions_gaais import questions
import random
import utils.sidebar as sidebar
import utils.database as db


sidebar.hide_sidebar()
db.init_db()

# Random order of the questions at first 
if "gaais_random" not in st.session_state:
    st.session_state["gaais_random"] = random.sample(questions, len(questions))

st.title("QUESTIONNAIRE 1")
st.write("")
st.markdown("""*Please rate how much you agree or disagree with each of the following statements. 
There are no right or wrong answers. Please respond based on your personal opinions.*""")
st.write("")
st.write("")

ordered_questions = st.session_state["gaais_random"]


options = [
    "Strongly Disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly Agree"
]

user_id = st.session_state["user_id"]


# The questions are shown vertically and the answers are shown horizontally
for question in ordered_questions:
    st.radio(
        question["text"],
        options=options,
        key=question["id"],
        index=None,
        horizontal=True, #make the answers horizontal
    )
    st.divider()


# Tek buton: Done
if st.button("Done",key="done_button1"):
    # Check if all questions are answered
    missing = [q["id"] for q in questions if st.session_state.get(q["id"]) is None]

    if missing:
        st.warning("Please answer all questions before proceeding.")
    else:
        db.create_participant_if_missing(
            user_id=user_id,
            group_no=int(st.session_state["group"]),
        )
        # Save all answers
        for question in questions:
            db.upsert_answer(
                user_id=user_id,
                survey="gaais",
                question_id=question["id"],
                answer=st.session_state[question["id"]],
            )
        st.success("All answers recorded. Thank you!")
        st.switch_page("pages/2_Chat.py")  # switch to the next page



        

    





