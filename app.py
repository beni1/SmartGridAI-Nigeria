import streamlit as st
import pandas as pd
import sys, os
import time
import matplotlib.pyplot as plt
import datetime

# Fix import path
sys.path.append(os.path.abspath("."))

from src.model import train_model, predict
from src.alerts import high_demand_alert

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="wide")

st.title("⚡ SmartGridAI Nigeria Dashboard")
st.caption("Real-time AI-powered electricity demand monitoring system")

st.divider()

# -----------------------------
# SIDEBAR (PROFESSIONAL)
# -----------------------------
st.sidebar.title("⚙️ Control Panel")

threshold = st.sidebar.slider("Alert Threshold", 100, 1000, 600)

st.sidebar.markdown("### About")
st.sidebar.write(
    "SmartGridAI monitors electricity demand in real time using machine learning."
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("data/demand_large.csv")

# Train model
X = df[["time"]]
y = df["consumption"]
model = train_model(X, y)

# -----------------------------
# REAL-TIME SYSTEM
# -----------------------------
st.subheader("⚡ Live SmartGridAI Monitoring")

# Session state
if "time_step" not in st.session_state:
    st.session_state.time_step = 1000

if "history" not in st.session_state:
    st.session_state.history = []

# OPTION A: Simulated time
st.session_state.time_step += 1
current_time = st.session_state.time_step

# OPTION B (REAL-WORLD TIME)
# current_time = datetime.datetime.now().hour

future_df = pd.DataFrame([[current_time]], columns=["time"])
prediction = predict(model, future_df)

# Store history
st.session_state.history.append(float(prediction[0]))
st.session_state.history = st.session_state.history[-50:]

# -----------------------------
# METRICS (PRO UI)
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Time", current_time)
col2.metric("Predicted Demand", f"{float(prediction[0]):.2f}")
col3.metric("Threshold", threshold)

st.divider()

# -----------------------------
# ALERT SYSTEM (CLEAN)
# -----------------------------
if high_demand_alert(prediction[0], threshold):
    st.error("⚠️ High Demand Detected")
else:
    st.success("✅ Grid Stable")

st.divider()

# -----------------------------
# LIVE CHART (IMPROVED)
# -----------------------------
st.subheader("📊 Real-Time Demand Trend")

fig, ax = plt.subplots()

ax.plot(st.session_state.history, linewidth=3)
ax.set_title("Electricity Demand Over Time")
ax.set_xlabel("Time Step")
ax.set_ylabel("Demand")
ax.grid(True)

st.pyplot(fig)

# -----------------------------
# AUTO REFRESH
# -----------------------------
time.sleep(2)
st.rerun()
