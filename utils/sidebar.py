import streamlit as st

def hide_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] {display: none !important;}
        [data-testid="stSidebar"][aria-expanded="false"] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

    
