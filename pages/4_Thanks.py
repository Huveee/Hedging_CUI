import streamlit as st
import utils.sidebar as sidebar
import utils.auth_helper as auth

sidebar.hide_sidebar()

user_id = auth.require_user_id()

st.markdown("""
# Thank you!

#### Your responses have been recorded.

#### You may now close this tab.

""")



