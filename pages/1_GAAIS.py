import streamlit as st
from data.questions_gaais import questions
import random
import utils.sidebar as sidebar
import utils.participant as participant

sidebar.hide_sidebar()


# Random order of the questions at first 
if "gaais_random" not in st.session_state:
    st.session_state["gaais_random"] = random.sample(questions, len(questions))

st.title("QUESTIONNAIRE 1")
st.markdown("""*Please rate how much you agree or disagree with each of the following statements. 
There are no right or wrong answers. Please respond based on your personal opinions.*""")

if "step" not in st.session_state:
    st.session_state.step = 0

current = st.session_state.step
ordered_questions = st.session_state["gaais_random"]
question = ordered_questions[current]

options = [
    "Strongly Disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly Agree"
]

user_id = st.session_state["user_id"]
file_answers = participant.load_answers(user_id)

saved_value = st.session_state.get(question["id"])
if saved_value is None:
    saved_value = file_answers.get(question["id"])
    # If the answer is in the file, save it in the session state
    if saved_value is not None:
        st.session_state[question["id"]] = saved_value

st.radio(
    question["text"], #show the question text
    options,
    index=options.index(saved_value) if saved_value in options else None,
    key=question["id"]) #save the answer in session state


col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if st.session_state.step > 0:
        if st.button("⬅ Back"):
            answer=st.session_state[question["id"]]
            participant.save_answer(user_id, question["id"], answer)
            st.session_state.step -= 1
            st.rerun()

with col3:
    if st.session_state.step < len(questions) - 1:
        if st.button("Next ➡"):
            answer=st.session_state[question["id"]]
            participant.save_answer(user_id, question["id"], answer)
            st.session_state.step += 1
            st.rerun()
    else:
        if st.button("Finish"):
            answer=st.session_state[question["id"]]
            participant.save_answer(user_id, question["id"], answer)
            missing_answers=False
            answers = participant.load_answers(user_id)  # zaten answers dict
            for answer in answers.values():
                if answer is None:
                    missing_answers=True
                    break
            if missing_answers:
                st.warning("Please answer all questions before proceeding.")
            else:

                st.success("All answers recorded. Thank you!")
                st.switch_page("pages/2_Chat.py")



        

    





