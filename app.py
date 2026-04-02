import streamlit as st
import pandas as pd
import sys, os
import time
import matplotlib.pyplot as plt

# Fix import path
sys.path.append(os.path.abspath("."))

from src.model import train_model, predict
from src.alerts import high_demand_alert

st.set_page_config(layout="wide")

st.title("⚡ SmartGridAI Nigeria Dashboard")

# Load data
df = pd.read_csv("data/demand_large.csv")

# Train model
X = df[["time"]]
y = df["consumption"]
model = train_model(X, y)

# -----------------------------
# USER CONTROL (IMPORTANT)
# -----------------------------
threshold = st.slider("Alert Threshold", 100, 1000, 600)

# -----------------------------
# REAL-TIME SYSTEM
# -----------------------------
st.subheader("⚡ Live SmartGridAI Monitoring")

if "time_step" not in st.session_state:
    st.session_state.time_step = 1000

if "history" not in st.session_state:
    st.session_state.history = []

# Update time
st.session_state.time_step += 1

future_df = pd.DataFrame([[st.session_state.time_step]], columns=["time"])
prediction = predict(model, future_df)

# Store history
st.session_state.history.append(float(prediction[0]))
st.session_state.history = st.session_state.history[-50:]

# Display
st.write("Time:", st.session_state.time_step)
st.write("Prediction:", float(prediction[0]))

# Alert (ONLY ONCE)
if high_demand_alert(prediction[0], threshold):
    st.warning("⚠️ HIGH DEMAND ALERT!")
else:
    st.success("✅ Demand is normal")

# -----------------------------
# LIVE CHART
# -----------------------------
st.subheader("📊 Live Demand Chart")

import matplotlib.pyplot as plt

st.subheader("📊 Live Demand Chart")

# Store data in session
if "history" not in st.session_state:
    st.session_state.history = []

# Add new prediction to history
st.session_state.history.append(float(prediction[0]))

# Limit size (last 50 points)
st.session_state.history = st.session_state.history[-50:]

# Plot
fig, ax = plt.subplots()
ax.plot(st.session_state.history, label="Live Prediction")
ax.set_title("Real-Time Demand")
ax.legend()

st.pyplot(fig)

# -----------------------------
# AUTO REFRESH (MUST BE LAST)
# -----------------------------
time.sleep(2)
st.rerun()