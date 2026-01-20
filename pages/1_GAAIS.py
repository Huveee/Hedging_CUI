import streamlit as st
from data.questions_gaais import questions
import random

if not st.session_state.get("consent_ok"):
    st.switch_page("Consent.py")

# Random order of the questions at first 
if "gaais_ordered" not in st.session_state:
    st.session_state["gaais_ordered"] = random.sample(questions, len(questions))

st.title("QUESTIONNAIRE 1")
st.markdown("""*Please rate how much you agree or disagree with each of the following statements. 
There are no right or wrong answers. Please respond based on your personal opinions.*""")

for question in st.session_state["gaais_ordered"]:
    st.radio(
        question["text"], #show the question text
        options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
        index=None, #No default answer selected
        key=question["id"]) #save the answer in session state



if st.button("Done"):
    st.session_state["gaais_ok"] = True
    st.switch_page("pages/2_Chat.py")
    missing_answers=False
    for question in st.session_state["gaais_ordered"]:
        if st.session_state.get(question["id"]) is None:
            missing_answers=True
            break
    if missing_answers:
        st.warning("Please answer all questions before proceeding.")
    else:
        st.success("All answers recorded. Thank you!")
        st.session_state["gaais_ok"] = True
        st.switch_page("pages/2_Chat.py")


        

    





