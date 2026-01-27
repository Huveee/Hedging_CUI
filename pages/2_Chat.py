import streamlit as st
import time
import utils.sidebar as sidebar

sidebar.hide_sidebar()


#State Initialization (To save the chat messages and final decision in case of rerunning the app)
# 1) Chat message history
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# 2) Chat start time (timestamp)
if "chat_started_at" not in st.session_state:
    st.session_state["chat_started_at"] = time.time()

# 3) Final decision (initially empty)
if "final_decision" not in st.session_state:
    st.session_state["final_decision"] = None

# 4) Decision submitted?
if "decision_submitted" not in st.session_state:
    st.session_state["decision_submitted"] = False

st.title("Decision Task")

st.markdown("""*Please read the following scenario carefully.  
After reading it, you can ask the assistant questions and then make your final decision.*""")

st.info("""**Imagine the following situation:**

You have €1,000 that you do not urgently need. A friend tells you about an investment opportunity in a new technology company.

If the company performs well, you could gain around 20% of your investment.
If it performs poorly, you could lose part of it.

You are unsure whether this is a good idea, so you may ask the assistant for advice before making your decision.""")


st.markdown("### Decision question")
st.markdown("**Should you invest in this option?**")

st.subheader("Chat")
chat_box=st.container()

with chat_box:
    for msg in st.session_state["chat_messages"]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Assistant:** {msg['content']}")


def send_message():
    text = st.session_state["user_input"].strip()
    if not text:
        return
    st.session_state["chat_messages"].append({"role": "user", "content": text})
    st.session_state["chat_messages"].append({"role": "assistant", "content": "Reply??..."})
    st.session_state["user_input"] = ""


st.text_input("Type your message here:", key="user_input")
st.button("Send", on_click=send_message)

st.subheader("Final decision")

decision = st.radio(
    "What do you decide?",
    ["Yes", "No"],
    key="final_decision",
    index=None
)

if st.button("Next"):
    # 1) Is there any user message?
    has_user_message = any(msg["role"] == "user" for msg in st.session_state["chat_messages"])

    if not has_user_message:
        st.error("Please ask at least one question in the chat before continuing.")
        st.stop()

    # 2) Final decision done?
    if st.session_state.get("final_decision") is None:
        st.error("Please make your final decision before continuing.")
        st.stop()

    # 3) If everything is done, switch to the next page
    st.switch_page("pages/3_Questionnaire.py")












