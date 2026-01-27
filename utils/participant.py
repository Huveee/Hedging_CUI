import streamlit as st
from uuid import uuid4
import json
import os
from streamlit_cookies_manager import EncryptedCookieManager


def init_participant():

    # If there is no participants folder, create it
    if not os.path.exists("participants"):
        os.makedirs("participants")

    # Create a cookie
    cookies = EncryptedCookieManager(
        prefix="my_study_",
        password="XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    )

    if not cookies.ready():
        st.stop()

    # Check if user ID exists
    user_id = cookies.get("user_id")

    if user_id is None:
        # New user → create unique ID
        user_id = str(uuid4())
        cookies["user_id"] = user_id
        cookies.save()

    st.write(f"Your participant ID: `{user_id}`")

    # Check if participant file exists
    filepath = f"participants/{user_id}.json"

    if os.path.exists(filepath):
        # Participant already completed the study → read the file
        with open(filepath, "r") as f:
            data = json.load(f)

    # If the participant has already completed the study, stop the app
    if data.get("completed") is True:
        st.error("You already completed the study.")
        st.stop()

    else:
        # New participant → assign group (0,1,2 loop)
        all_files = os.listdir("participants")
        participant_count = len(all_files)
        assigned_group = participant_count % 3  # 0,1,2

        data = {
            "user_id": user_id,
            "group": assigned_group,
            "completed": False, #For checking if the participant has completed the study
            "answers": {}      # For saving the participant's answers
        }

        # Save the file
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        st.success(f"You have been assigned to **group {assigned_group}**")

    # Save the group in Streamlit session state
    st.session_state["group"] = data["group"]
    # Save the user ID in Streamlit session state
    st.session_state["user_id"] = user_id


def save_answer(user_id: str, question_id: str, answer):
    path = f"participants/{user_id}.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)  # Load the file

    if "answers" not in data or not isinstance(data["answers"], dict):
        data["answers"] = {}  # Initialize the answers dictionary if it doesn't exist

    data["answers"][question_id] = answer

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)  # Save the file



def load_answers(user_id: str) -> dict:
    path = f"participants/{user_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("answers", {})


