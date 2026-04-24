import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from stream_engine import generate_demand
from state_manager import init_state, update_state
from visuals import build_chart
from config import REFRESH_INTERVAL

# LSTM IMPORT
from lstm_model import train_lstm, predict_next

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="SmartGridAI", layout="wide")

st.title("⚡ SmartGridAI - Live Demand Dashboard (AI Mode)")
st.markdown("### ⚡ Predict. Monitor. Optimize Energy")

# =========================
# INIT STATE
# =========================
init_state()

# =========================
# BUILD DATAFRAME FROM STATE
# =========================
df = pd.DataFrame({
    "time": range(len(st.session_state.data)),
    "consumption": st.session_state.data
})

# =========================
# STEP 1 — ADD TIME-SERIES FEATURES
# =========================
if len(df) > 5:
    df["lag1"] = df["consumption"].shift(1)
    df["lag2"] = df["consumption"].shift(2)
    df["rolling_mean"] = df["consumption"].rolling(3).mean()
    df = df.dropna()
else:
    df["lag1"] = df["consumption"]
    df["lag2"] = df["consumption"]
    df["rolling_mean"] = df["consumption"]

# =========================
# STEP 2 — RANDOM FOREST MODEL
# =========================
if len(df) > 5:
    X = df[["time", "lag1", "lag2", "rolling_mean"]]
    y = df["consumption"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.header("Controls")

auto_mode = st.sidebar.checkbox("Enable Auto Refresh (Click-based Simulation)")
threshold = st.sidebar.slider("Alert Threshold", 100, 1000, 500)

use_lstm = st.sidebar.checkbox("Use LSTM Prediction")

# =========================
# DATA GENERATION
# =========================
if st.sidebar.button("Generate Next Data Point"):
    value = generate_demand(st.session_state.t)
    update_state(value)

if auto_mode:
    value = generate_demand(st.session_state.t)
    update_state(value)
    st.info("Auto mode ON: Click '🔄 Refresh Now' to stream next data point")
    st.button("🔄 Refresh Now")

# =========================
# STEP 3 — LIVE AI PREDICTION
# =========================
if use_lstm and len(df) > 10:
    series = df["consumption"].values[-50:]

    lstm_model = train_lstm(series)

    last_window = series[-10:]
    live_pred = predict_next(lstm_model, last_window)

elif len(df) > 5:
    last = df.iloc[-1]

    input_data = [[
        len(df),
        last["consumption"],
        last["lag1"],
        last["rolling_mean"]
    ]]

    live_pred = float(model.predict(input_data)[0])

else:
    live_pred = st.session_state.data[-1] if len(st.session_state.data) > 0 else 0

# =========================
# STEP 4 — ANOMALY DETECTION
# =========================
if len(df) > 5:
    mean_demand = df["consumption"].mean()
    std_demand = df["consumption"].std()
    is_anomaly = live_pred > (mean_demand + 2 * std_demand)
else:
    mean_demand = 0
    std_demand = 0
    is_anomaly = False

# =========================
# STEP 5 — ALERT LOGIC
# =========================
alert_triggered = live_pred > threshold or is_anomaly

# =========================
# MAIN DASHBOARD
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📈 Live Demand Stream")

    if len(st.session_state.data) > 0:
        chart_df = build_chart(st.session_state.time, st.session_state.data)
        st.line_chart(chart_df.set_index("Time"))
    else:
        st.warning("No data yet. Click Generate.")

with col2:
    st.subheader("📊 Stats")

    if len(st.session_state.data) > 0:
        st.metric("Current Demand", st.session_state.data[-1])
        st.metric("AI Predicted", int(live_pred))
        st.metric("Total Points", len(st.session_state.data))
    else:
        st.write("No data yet")

# =========================
# STEP 6 — ALERTS
# =========================
if alert_triggered:
    st.error("⚠️ ALERT: High Demand or Anomaly Detected")

if is_anomaly:
    st.error("🚨 AI DETECTED ANOMALY (UNUSUAL SPIKE)")

# =========================
# STEP 7 — TREND
# =========================
if len(st.session_state.data) > 5:
    recent = st.session_state.data[-5:]

    if recent[-1] > recent[0]:
        st.warning("📈 Rising Demand Trend")
    else:
        st.info("📉 Stable or Falling Trend")

# =========================
# STEP 8 — INSIGHTS
# =========================
st.subheader("🧠 AI Insights")

st.write(f"Average Demand: {int(mean_demand)}")
st.write(f"Demand Volatility: {int(std_demand)}")

# =========================
# DEBUG
# =========================
st.write("Auto mode:", auto_mode)
st.write("Data points:", len(st.session_state.data))
st.write("Current t:", st.session_state.t)

# =========================
# FOOTER
# =========================
st.caption("SmartGridAI Nigeria - Phase 2 AI Mode (Anomaly + Prediction Enabled)")
