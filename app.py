import streamlit as st

from stream_engine import generate_demand
from state_manager import init_state, update_state
from visuals import build_chart
from config import REFRESH_INTERVAL

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="SmartGridAI", layout="wide")

st.title("⚡ SmartGridAI - Live Demand Dashboard (Stable Mode)")

# =========================
# INIT STATE
# =========================
init_state()

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.header("Controls")

auto_mode = st.sidebar.checkbox("Enable Auto Refresh (Click-based Simulation)")

# manual trigger (safe streaming)
if st.sidebar.button("Generate Next Data Point"):
    value = generate_demand(st.session_state.t)
    update_state(value)

# auto mode (SAFE version)
if auto_mode:
    value = generate_demand(st.session_state.t)
    update_state(value)

    st.info("Auto mode ON: Click rerun to continue streaming")
    st.button("🔄 Refresh Now")

# =========================
# DEBUG / SANITY CHECK
# =========================
st.write("Auto mode:", auto_mode)
st.write("Data points:", len(st.session_state.data))
st.write("Current t:", st.session_state.t)

# =========================
# MAIN DASHBOARD
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📈 Live Demand Stream")

    if len(st.session_state.data) > 0:
        df = build_chart(st.session_state.time, st.session_state.data)
        st.line_chart(df.set_index("Time"))
    else:
        st.warning("No data yet. Click Generate.")

with col2:
    st.subheader("📊 Stats")

    if len(st.session_state.data) > 0:
        st.metric("Current Demand", st.session_state.data[-1])
        st.metric("Total Points", len(st.session_state.data))
    else:
        st.write("No data yet")

# =========================
# FOOTER
# =========================
st.caption("SmartGridAI Nigeria - Phase 1.5 Stable Mode (No Thread Loops)")