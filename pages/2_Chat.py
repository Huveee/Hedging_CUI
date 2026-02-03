import streamlit as st
import time
import utils.sidebar as sidebar
import utils.database as db
from data.scenarios import DECISION_SCENARIO, DECISION_QUESTION


import requests  # For Ollama API calls
import json

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:1b"


sidebar.hide_sidebar()
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
chat_box=st.container()

with chat_box:
    for msg in st.session_state["chat_messages"]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Assistant:** {msg['content']}")



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


def send_message():
    text = st.session_state["user_input"].strip()
    if not text:
        return

    # user mesajı
    st.session_state["chat_messages"].append(
        {"role": "user", "content": text}
    )
    st.session_state["user_input"] = ""

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


    for m in st.session_state["chat_messages"]:
        messages.append(
            {"role": m["role"], "content": m["content"]}
        )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=60
        )
        r.raise_for_status()
        data = r.json()

        assistant_reply = data["message"]["content"]

    except Exception as e:
        assistant_reply = f"(Ollama error: {e})"

    # assistant cevabı
    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": assistant_reply}
    )



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

    # DB: make sure participant row exists 
    db.create_participant_if_missing(
        user_id=st.session_state["user_id"],
        group_no=int(st.session_state["group"])
    )

    # DB: save decision
    db.set_decision(
        user_id=st.session_state["user_id"],
        decision=st.session_state["final_decision"]
    )

    # 4) If everything is done, switch to the next page
    st.switch_page("pages/3_Questionnaire.py")












