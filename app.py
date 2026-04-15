import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import datetime
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="SmartGridAI", layout="wide")

st.title("⚡ SmartGridAI - Live Grid Monitor")
st.markdown("Real-Time AI Energy Monitoring System")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Controls")

num_days = st.sidebar.slider("Forecast Days", 1, 30, 7)
temp_input = st.sidebar.slider("Base Temperature (°C)", 20, 45, 30)
threshold = st.sidebar.slider("Alert Threshold (MW)", 100, 1000, 500)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return pd.read_csv("data/demand_large.csv")

df = load_data()

# =========================
# MODEL
# =========================
X = df[["time", "temperature"]]
y = df["consumption"]

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

# =========================
# SESSION STATE (LIVE STREAM BUFFER)
# =========================
if "live_data" not in st.session_state:
    st.session_state.live_data = []

if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False

# =========================
# GENERATE LIVE DATA POINT
# =========================
live_temp = temp_input + np.random.normal(0, 1)

live_demand = model.predict([[len(df), live_temp]])[0]

current_time = datetime.datetime.now()

# store last 50 points (rolling window)
st.session_state.live_data.append({
    "time": current_time,
    "demand": live_demand
})

st.session_state.live_data = st.session_state.live_data[-50:]

live_df = pd.DataFrame(st.session_state.live_data)

# =========================
# LIVE STATUS ENGINE
# =========================
if live_demand > threshold:
    status = "🔴 CRITICAL"
else:
    status = "🟢 NORMAL"

# =========================
# LIVE DASHBOARD
# =========================
st.subheader("⚡ Live Grid Status")

col1, col2, col3 = st.columns(3)

col1.metric("Live Demand", f"{int(live_demand)} MW")
col2.metric("Grid Status", status)
col3.metric("Threshold", f"{threshold} MW")

# =========================
# ALERT ENGINE (ANTI-SPAM)
# =========================
if live_demand > threshold:
    st.error("⚠️ LIVE GRID ALERT")

    if not st.session_state.alert_sent:
        st.warning("🚨 Alert Triggered")
        st.session_state.alert_sent = True

else:
    st.success("✔ Grid Stable")
    st.session_state.alert_sent = False

# =========================
# LIVE STREAM CHART
# =========================
st.subheader("📊 Live Demand Stream")

if not live_df.empty:
    chart_df = live_df.set_index("time")

    # Add threshold line
    chart_df["threshold"] = threshold

    st.line_chart(chart_df)

# =========================
# FORECAST (STILL AVAILABLE)
# =========================
st.subheader("📈 Forecast")

future_time = np.arange(len(df), len(df) + num_days)
future_temp = np.full(num_days, temp_input)

future_df = pd.DataFrame({
    "time": future_time,
    "temperature": future_temp
})

predictions = model.predict(future_df)

forecast_df = pd.DataFrame({
    "Day": range(num_days),
    "Prediction": predictions,
    "Threshold": [threshold] * num_days
})

st.line_chart(forecast_df.set_index("Day"))

# =========================
# CONTROL BUTTON (SIMULATE STREAM STEP)
# =========================
st.subheader("🧪 Control")

if st.button("▶️ Generate Next Data Point"):
    st.rerun()

# =========================
# AUTO MODE (OPTIONAL)
# =========================
auto_mode = st.checkbox("Enable Auto Refresh (Real-Time Mode)")

if auto_mode:
    import time
    time.sleep(2)
    st.rerun()

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("🟢 SmartGridAI Live Engine Running | Real-Time Mode Enabled")