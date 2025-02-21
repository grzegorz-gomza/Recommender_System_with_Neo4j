import streamlit as st
import io

# from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit.runtime.scriptrunner import get_script_run_ctx


def write_message(role, content, save=True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})

    # Write to UI
    with st.chat_message(role):
        st.markdown(content)


def get_session_id():
    return get_script_run_ctx().session_id


import ast


def clean_uploaded_data(byte_data):
    """
    Cleans the byte string data and converts it into a proper Python list.

    Parameters:
        byte_data (bytes): Byte string, e.g., b"['film1']\r\n"

    Returns:
        list: Python list extracted from the byte string.
    """
    # Decode the byte string to a regular string
    decoded_str = byte_data.decode("utf-8").strip()

    # Safely evaluate the string as a Python literal (list)
    python_list = ast.literal_eval(decoded_str)

    return python_list


def initialize_session_state():
    # Set up Session State
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_movies" not in st.session_state:
        st.session_state.user_movies = []
    if "user_actors" not in st.session_state:
        st.session_state.user_actors = []
    if "user_genres" not in st.session_state:
        st.session_state.user_genres = []
    if "user_watched" not in st.session_state:
        st.session_state.user_watched = []

def check_if_session_state_empty():
    if all(
        [
            st.session_state.user_movies == [],
            st.session_state.user_actors == [],
            st.session_state.user_genres == [],
            st.session_state.user_watched == [],
        ]
    ):
        return True
    return False
