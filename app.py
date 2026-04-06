import streamlit as st
import pandas as pd
import sys, os
import time
import matplotlib.pyplot as plt
import datetime
import requests

# Fix import path
sys.path.append(os.path.abspath("."))

from src.model import train_model, predict
from src.alerts import high_demand_alert

# -----------------------------
# PAGE CONFIG + STYLE (FINTECH UI)
# -----------------------------
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    body { background-color: #0E1117; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚡ SmartGridAI Nigeria Dashboard")
st.caption("Real-time AI-powered electricity demand monitoring system")

st.divider()

# -----------------------------
# WEATHER API FUNCTION
# -----------------------------
def get_weather():
    API_KEY = "e18d33bd3d9e2e32a24a560bb6382ceb"
    city = "Lagos"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()
        temp = data["main"]["temp"]
        return temp
    except:
        return 30  # fallback value

# -----------------------------
# SIDEBAR (PRO UI)
# -----------------------------
st.sidebar.title("⚙️ Control Panel")

threshold = st.sidebar.slider("Alert Threshold", 100, 1000, 600)

temperature = get_weather()
st.sidebar.metric("🌡️ Lagos Temp", f"{temperature}°C")

st.sidebar.markdown("### About")
st.sidebar.write(
    "SmartGridAI monitors electricity demand using AI + real-time weather data."
)

# -----------------------------
# LOAD DATA + MODEL
# -----------------------------
df = pd.read_csv("data/demand_large.csv")

X = df[["time"]]
y = df["consumption"]
model = train_model(X, y)

# -----------------------------
# REAL-TIME SYSTEM
# -----------------------------
st.subheader("⚡ Live SmartGridAI Monitoring")

if "time_step" not in st.session_state:
    st.session_state.time_step = 1000

if "history" not in st.session_state:
    st.session_state.history = []

# Time update
st.session_state.time_step += 1
current_time = st.session_state.time_step

# Prediction (you can later include temperature as feature)
future_df = pd.DataFrame([[current_time]], columns=["time"])
prediction = predict(model, future_df)

# Store history
st.session_state.history.append(float(prediction[0]))
st.session_state.history = st.session_state.history[-50:]

# -----------------------------
# METRICS (FINTECH STYLE)
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("⏱ Time", current_time)
col2.metric("⚡ Demand", f"{float(prediction[0]):.2f}")
col3.metric("🚨 Threshold", threshold)

st.divider()

# -----------------------------
# ALERT SYSTEM
# -----------------------------
if high_demand_alert(prediction[0], threshold):
    st.error("🚨 GRID OVERLOAD RISK")
else:
    st.success("🟢 GRID STABLE")

st.divider()

# -----------------------------
# CHART (FINTECH STYLE)
# -----------------------------
st.subheader("📊 Real-Time Demand Trend")

fig, ax = plt.subplots()

ax.plot(st.session_state.history, linewidth=3)
ax.set_facecolor("#111")
ax.set_title("Electricity Demand Over Time")
ax.set_xlabel("Time Step")
ax.set_ylabel("Demand")
ax.grid(color="gray", linestyle="--", linewidth=0.5)

st.pyplot(fig)

# -----------------------------
# AUTO REFRESH
# -----------------------------
time.sleep(2)
st.rerun()
