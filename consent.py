import streamlit as st
import utils.sidebar as sidebar
import uuid
import utils.database as db
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    prefix="study_",
    password="XXXXXXXXXXXXXXXXXXXX"
)

if not cookies.ready():
    st.stop()


#To hide the sidebar with the function we created
sidebar.hide_sidebar()
db.init_db()


# If user_id doesn't exist in cookies, create it
if "user_id" not in cookies:
    cookies["user_id"] = str(uuid.uuid4())
    cookies.save()

st.session_state["user_id"] = cookies["user_id"]

# If user already completed, block (same browser shouldn't complete twice)
if db.is_completed(st.session_state["user_id"]):
    st.error("You have already completed this study in this browser.")
    st.stop()


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



# Assign group if missing (0/1/2)
if "group" not in st.session_state:
    # simple random assignment
    st.session_state["group"] = uuid.uuid4().int % 3

st.write("")

agree = st.checkbox("I agree")


if agree:   
    if st.button("Go"):
        # Create participant row in DB
        db.create_participant_if_missing(
            user_id=st.session_state["user_id"],
            group_no=int(st.session_state["group"])
        )
        st.switch_page("pages/1_GAAIS.py")

