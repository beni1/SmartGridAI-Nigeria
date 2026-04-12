import pandas as pd
import numpy as np
import streamlit as st
import time
import requests
import smtplib
from email.mime.text import MIMEText

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

st.title("⚡ SmartGridAI - Intelligent Energy Dashboard")

# =========================
# SIDEBAR (PRO UI)
# =========================
st.sidebar.header("⚙️ Controls")

threshold_multiplier = st.sidebar.slider("Alert Sensitivity", 1.0, 3.0, 2.0)
num_points = st.sidebar.slider("Data Points", 50, 500, 200)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/demand_large.csv")

# =========================
# 🌍 REAL-TIME DATA (Weather API)
# =========================
try:
    url = "https://api.open-meteo.com/v1/forecast?latitude=60.17&longitude=24.94&current_weather=true"
    data = requests.get(url).json()
    live_temp = data["current_weather"]["temperature"]
    st.sidebar.write(f"🌡️ Live Temp: {live_temp}°C")
    df["temperature"].iloc[-1] = live_temp
except:
    st.sidebar.write("⚠️ Live weather unavailable")

# =========================
# FEATURE ENGINEERING
# =========================
df["time_squared"] = df["time"] ** 2
df["sin_time"] = np.sin(df["time"] / 10)
df["cos_time"] = np.cos(df["time"] / 10)

df["lag_1"] = df["consumption"].shift(1)
df["lag_2"] = df["consumption"].shift(2)
df["lag_3"] = df["consumption"].shift(3)

df["rolling_mean"] = df["consumption"].rolling(window=5).mean()
df["rolling_std"] = df["consumption"].rolling(window=5).std()

df = df.dropna()

# =========================
# MODELS
# =========================
features = [
    "time", "temperature",
    "time_squared", "sin_time", "cos_time",
    "lag_1", "lag_2", "lag_3",
    "rolling_mean", "rolling_std"
]

X = df[features]
y = df["consumption"]

# RandomForest
rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
rf_model.fit(X, y)
df["rf_pred"] = rf_model.predict(X)

# Linear Regression (comparison)
lr_model = LinearRegression()
lr_model.fit(X, y)
df["lr_pred"] = lr_model.predict(X)

# =========================
# ALERT SYSTEM
# =========================
threshold = df["consumption"].mean() + threshold_multiplier * df["consumption"].std()
df["alert"] = df["rf_pred"] > threshold

# =========================
# 📩 EMAIL FUNCTION
# =========================
def send_email_alert(message):
    sender = "your_email@gmail.com"
    password = "your_app_password"
    receiver = "receiver_email@gmail.com"

    msg = MIMEText(message)
    msg["Subject"] = "⚡ SmartGrid Alert"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        st.success("📩 Email Sent!")
    except Exception as e:
        st.error(f"Email failed: {e}")

# =========================
# DASHBOARD
# =========================
st.subheader("📊 Model Comparison")
st.line_chart(df.tail(num_points)[["consumption", "rf_pred", "lr_pred"]])

st.subheader("🌡️ Temperature vs Consumption")
st.scatter_chart(df[["temperature", "consumption"]])

# KPIs
st.metric("⚡ Current Demand", int(df["consumption"].iloc[-1]))
st.metric("🔮 RF Prediction", int(df["rf_pred"].iloc[-1]))

# =========================
# FUTURE FORECAST
# =========================
future_steps = 20
last_row = df.iloc[-1].copy()
future_predictions = []

for i in range(future_steps):
    new_time = last_row["time"] + 1
    new_temp = 28 + 5 * np.sin(new_time / 50)

    new_row = {
        "time": new_time,
        "temperature": new_temp,
        "time_squared": new_time ** 2,
        "sin_time": np.sin(new_time / 10),
        "cos_time": np.cos(new_time / 10),
        "lag_1": last_row["consumption"],
        "lag_2": last_row["lag_1"],
        "lag_3": last_row["lag_2"],
        "rolling_mean": df["consumption"].tail(5).mean(),
        "rolling_std": df["consumption"].tail(5).std()
    }

    pred = rf_model.predict(pd.DataFrame([new_row]))[0]
    future_predictions.append(pred)

    last_row["lag_2"] = last_row["lag_1"]
    last_row["lag_1"] = last_row["consumption"]
    last_row["consumption"] = pred
    last_row["time"] = new_time

future_df = pd.DataFrame({"predicted": future_predictions})

st.subheader("🔮 Future Forecast")
st.line_chart(future_df)

# =========================
# ALERTS
# =========================
st.subheader("🚨 High Demand Alerts")

alerts = df[df["alert"] == True]

if not alerts.empty:
    st.warning("⚠️ High Demand Detected!")
    st.dataframe(alerts)

    # Send email
    if st.button("Send Alert Email"):
        send_email_alert("⚠️ High energy demand detected!")

else:
    st.success("✅ System Stable")

# =========================
# RAW DATA
# =========================
if st.checkbox("Show Raw Data"):
    st.dataframe(df)

# =========================
# 🔄 AUTO REFRESH (REAL-TIME SIMULATION)
# =========================
time.sleep(5)
st.rerun()
