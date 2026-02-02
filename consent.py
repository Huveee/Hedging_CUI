import streamlit as st
import utils.sidebar as sidebar
import utils.participant as participant


#To hide the sidebar with the function we created
sidebar.hide_sidebar()


st.title("HELLO")
st.write("")
st.subheader("Participant Information and Consent")
st.markdown("""
You are invited to participate in an online research study on decision-making
and interactions with AI-based advisors.

Your participation is voluntary, and you may leave the study at any time.

You will read a fictional financial decision scenario, interact with a chatbot,
make a final decision, and complete short questionnaires.

No personal identifying information will be collected. Your responses will be
stored anonymously using a random participant ID and used only for research purposes.
""")

participant.init_participant()
agree = st.checkbox("I agree")


if agree:   
    if st.button("Go"):
        st.switch_page("pages/1_GAAIS.py")

