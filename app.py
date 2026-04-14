import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import yagmail
import os
import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="SmartGridAI", layout="wide")

# =========================
# TITLE
# =========================
st.title("⚡ SmartGridAI Dashboard")
st.markdown("AI-powered Energy Demand Forecasting & Alert System")

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.header("Controls")

num_days = st.sidebar.slider("Select Days", 1, 30, 7)
temp_input = st.sidebar.slider("Temperature (°C)", 20, 45, 30)
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
# PREDICTION
# =========================
future_time = np.arange(len(df), len(df) + num_days)
future_temp = np.full(num_days, temp_input)

future_df = pd.DataFrame({
    "time": future_time,
    "temperature": future_temp
})

predictions = model.predict(future_df)
peak_demand = int(np.max(predictions))

# =========================
# METRICS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Avg Demand", f"{int(np.mean(predictions))} MW")
col2.metric("Peak Demand", f"{peak_demand} MW")
col3.metric("Min Demand", f"{int(np.min(predictions))} MW")

# =========================
# ALERT STATUS BADGE
# =========================
if peak_demand > threshold:
    st.error("🔴 Alert Status: CRITICAL")
else:
    st.success("🟢 Alert Status: NORMAL")

# =========================
# CHART WITH THRESHOLD LINE
# =========================
st.subheader("📊 Demand Forecast")

chart_df = pd.DataFrame({
    "Day": range(num_days),
    "Predicted Demand": predictions,
    "Threshold": [threshold] * num_days
})

st.line_chart(chart_df.set_index("Day"))

# =========================
# TABLE
# =========================
st.subheader("📋 Forecast Data")
st.dataframe(chart_df)

# =========================
# SUBSCRIPTION SYSTEM
# =========================
st.subheader("📩 Subscribe for Alerts")

subscriber_email = st.text_input("Enter your email")

def save_subscriber(email):
    if email:
        with open("subscribers.txt", "a+") as f:
            f.seek(0)
            emails = f.read().splitlines()
            if email not in emails:
                f.write(email + "\n")
                return True
    return False

if st.button("Subscribe"):
    if save_subscriber(subscriber_email):
        st.success("✅ Subscribed successfully!")
    else:
        st.warning("⚠️ Already subscribed or invalid input")

def get_subscribers():
    try:
        with open("subscribers.txt", "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

# =========================
# EMAIL FUNCTION
# =========================
def send_bulk_alert(message, subject):
    try:
        yag = yagmail.SMTP(
            user=os.getenv("EMAIL_USER"),
            password=os.getenv("EMAIL_PASS")
        )

        subscribers = get_subscribers()

        for email in subscribers:
            yag.send(
                to=email,
                subject=subject,
                contents=message
            )

        return True, len(subscribers)

    except Exception as e:
        return False, str(e)

# =========================
# ALERT LOGGING
# =========================
def log_alert(demand, threshold):
    log_entry = pd.DataFrame([{
        "time": datetime.datetime.now(),
        "demand": demand,
        "threshold": threshold
    }])

    try:
        log_entry.to_csv("alerts.csv", mode="a", header=not os.path.exists("alerts.csv"), index=False)
    except:
        pass

# =========================
# ALERT LOGIC (ANTI-SPAM)
# =========================
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False

if peak_demand > threshold:
    st.error("⚠️ High Demand Alert!")

    if not st.session_state.alert_sent:
        message = f"""
⚡ SMART GRID ALERT ⚡

High energy demand detected!

Demand: {peak_demand} MW
Threshold: {threshold} MW
Time: {current_time}

Action: Monitor grid or activate backup supply.
"""

        subject = f"⚠️ High Energy Demand Alert ({peak_demand} MW)"

        success, info = send_bulk_alert(message, subject)

        if success:
            st.success(f"📧 Alert sent to {info} subscribers!")
            log_alert(peak_demand, threshold)
            st.session_state.alert_sent = True
        else:
            st.warning(f"Email failed: {info}")

else:
    st.session_state.alert_sent = False

# =========================
# TEST BUTTON
# =========================
st.subheader("🧪 Test Alert System")

if st.button("Send Test Alert to Subscribers"):
    success, info = send_bulk_alert(
        "Test alert from SmartGridAI 🚀",
        "🧪 SmartGridAI Test Alert"
    )

    if success:
        st.success(f"Test email sent to {info} subscribers!")
    else:
        st.error(f"Error: {info}")
