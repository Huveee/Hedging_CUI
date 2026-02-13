import streamlit as st
import time
import utils.sidebar as sidebar
import utils.database as db
import utils.auth_helper as auth
from data.scenarios import DECISION_SCENARIO, DECISION_QUESTION
from components.chat_render import render_chat

import requests  # For API calls
import json

import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://chat-ai.academiccloud.de/v1/chat/completions"
API_KEY = os.getenv("API_KEY") 
if not API_KEY:
    st.error("API_KEY not found. Please set it in the .env file.")
    st.stop()
    
MODEL_NAME = "llama-3.3-70b-instruct"  


sidebar.hide_sidebar()
user_id = auth.require_user_id()
db.init_db()


#State Initialization (To save the chat messages and final decision in case of rerunning the app)
# Chat message history
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# Chat start time (timestamp)
if "chat_started_at" not in st.session_state:
    st.session_state["chat_started_at"] = time.time()

# Final decision
if "final_decision" not in st.session_state:
    st.session_state["final_decision"] = None

# check if the decision submitted
if "decision_submitted" not in st.session_state:
    st.session_state["decision_submitted"] = False

if "waiting_for_response" not in st.session_state:
    st.session_state["waiting_for_response"] = False

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



def get_ai_response() -> str:
    # System + old messages
    group = int(st.session_state.get("group", 0))

    messages = [
        {
            "role": "system",
            "content": system_prompt_for_group(group)
        },    
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

    return assistant_reply


chat_slot = st.container()
with chat_slot:
    # Chat Window
    loading = st.session_state.get("waiting_for_response", False)
    
    # Render existing messages + loading indicator if needed
    render_chat(st.session_state["chat_messages"], loading=loading)

    # If we are in loading state, perform the API call now
    if loading:
        response = get_ai_response()
        
        # Add assistant response
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": response}
        )
        
        # Reset loading state
        st.session_state["waiting_for_response"] = False
        
        # Rerun to show the new message and remove loading indicator
        st.rerun()


# adding space between chat box and input area
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
    
    # Only append user message and set waiting flag
    st.session_state["chat_messages"].append({"role": "user", "content": clean})
    st.session_state["waiting_for_response"] = True
    # The script will rerun after this callback, picking up the waiting state


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
    # Check if there any user message
    has_user_message = any(msg["role"] == "user" for msg in st.session_state["chat_messages"])

    if not has_user_message:
        st.error("Please ask at least one question in the chat before continuing.")
        st.stop()

    # Check if the final decision selected
    if st.session_state.get("final_decision") is None:
        st.error("Please make your final decision before continuing.")
        st.stop()

    # make sure participant row exists in db
    db.create_participant_if_missing(
        user_id=user_id,
        group_no=int(st.session_state["group"])
    )

    # save decision to db
    db.set_decision(
        user_id=user_id,
        decision=st.session_state["final_decision"]
    )

    # If everything is done, switch to the next page
    st.switch_page("pages/3_Questionnaire.py")












