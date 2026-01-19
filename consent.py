import streamlit as st
st.title("HELLO")
with st.expander("Participant Information and Consent", expanded=True):
    st.markdown("""
    You are invited to participate in an online research study on decision-making
    and interactions with AI-based advisors.

    Your participation is voluntary, and you may leave the study at any time.

    You will read a fictional financial decision scenario, interact with a chatbot,
    make a final decision, and complete short questionnaires.

    No personal identifying information will be collected. Your responses will be
    stored anonymously using a random participant ID and used only for research purposes.
    """)

agree = st.checkbox("I agree")

if agree:
    st.write("Great!")
    if st.button("Go"):
         st.switch_page("pages/GAAIS.py")

