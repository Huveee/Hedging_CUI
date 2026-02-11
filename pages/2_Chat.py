import streamlit as st
import time
import utils.sidebar as sidebar
import utils.database as db
import utils.auth_helper as auth
from data.scenarios import DECISION_SCENARIO, DECISION_QUESTION
from components.chat_render import render_chat

import requests  # For API calls
import json

API_URL = "https://chat-ai.academiccloud.de/v1/chat/completions"
API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
MODEL_NAME = "llama-3.3-70b-instruct"  


sidebar.hide_sidebar()
user_id = auth.require_user_id()
db.init_db()


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
st.write("")

st.markdown("""*Please read the following scenario carefully.  
After reading it, you can ask the assistant questions and then make your final decision.*""")
st.write("")

st.info(f"***Imagine the following situation:***\n\n{DECISION_SCENARIO}")

st.markdown("### Decision question")
st.markdown(f"**{DECISION_QUESTION}**")

st.subheader("Chat")
st.write("Your group is: ", st.session_state["group"])


# Assign system prompt for different groups
def system_prompt_for_group(group: int) -> str: 
    if group == 0:
        return (
            "You are a helpful assistant. Answer clearly and briefly. "
            "Give practical pros/cons and a balanced recommendation."
        )
    if group == 1:
        return (
            "You are a cautious assistant. Avoid overconfidence. "
            "If information is missing, say so. Use hedging when appropriate "
            "(e.g., 'it depends', 'might', 'uncertain'). Provide pros/cons."
        )
    if group == 2:
        return (
            "You are a Socratic assistant. Ask 1-3 clarifying questions first "
            "before giving advice. Then provide pros/cons and a recommendation."
        )
    return "You are a helpful assistant."



def send_message(text: str):
    text = text.strip()
    if not text:
        return

    # save the user message
    st.session_state["chat_messages"].append(
        {"role": "user", "content": text}
    )

    # System + old messages
    group = int(st.session_state.get("group", 0))

    messages = [
        {
            "role": "system",
            "content": system_prompt_for_group(group)
        },    
        # {
        #     "role": "system",
        #     "content": f"SCENARIO CONTEXT:\n{DECISION_SCENARIO}"
        # },
        # {
        #     "role": "system",
        #     "content": f"DECISION QUESTION:\n{DECISION_QUESTION}"
        # }
    ]

    # add the past messages
    messages.extend(st.session_state["chat_messages"])

    # PAYLOAD
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "stream": False
    }

    # HEADER
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        r.raise_for_status()
        data = r.json()

        assistant_reply = data["choices"][0]["message"]["content"]

    except Exception as e:
        assistant_reply = f"(API error: {e})"

    # add the message of the assistant
    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": assistant_reply}
    )


# --- Chat Window ---
render_chat(st.session_state["chat_messages"])

# adding space between chat box and input
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

if "draft" not in st.session_state:
    st.session_state["draft"] = ""
if "input_error" not in st.session_state:
    st.session_state["input_error"] = False


def handle_send():
    clean = (st.session_state.get("draft") or "").strip()
    if clean == "":
        st.session_state["input_error"] = True
        return

    st.session_state["input_error"] = False
    st.session_state["draft"] = ""
    send_message(clean)
    st.rerun()


col1, col2 = st.columns([6, 1])

with col1:
    st.text_input(
        label="Message",
        key="draft",
        label_visibility="collapsed",
        placeholder="Write your message…",
    )

with col2:
    st.button("Send", type="primary", on_click=handle_send)

# Dont let user to send empty message
if st.session_state["input_error"]:
    st.error("You cannot send empty message. Please write something.")


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

    # DB: make sure participant row exists 
    db.create_participant_if_missing(
        user_id=user_id,
        group_no=int(st.session_state["group"])
    )

    # DB: save decision
    db.set_decision(
        user_id=user_id,
        decision=st.session_state["final_decision"]
    )

    # 4) If everything is done, switch to the next page
    st.switch_page("pages/3_Questionnaire.py")












