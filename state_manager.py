# state_manager.py
import streamlit as st
from config import MAX_POINTS

def init_state():
    if "data" not in st.session_state:
        st.session_state.data = []

    if "time" not in st.session_state:
        st.session_state.time = []

    if "t" not in st.session_state:
        st.session_state.t = 0


def update_state(value):
    st.session_state.t += 1

    st.session_state.data.append(value)
    st.session_state.time.append(st.session_state.t)

    # limit memory growth
    if len(st.session_state.data) > MAX_POINTS:
        st.session_state.data.pop(0)
        st.session_state.time.pop(0)