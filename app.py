import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

st.title("⚡ SmartGridAI - Advanced Time-Series Dashboard (No LSTM)")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/demand_large.csv")

# =========================
# FEATURE ENGINEERING (TIME INTELLIGENCE)
# =========================
df["time_squared"] = df["time"] ** 2
df["sin_time"] = np.sin(df["time"] / 10)
df["cos_time"] = np.cos(df["time"] / 10)

# 🔥 LAG FEATURES (THIS REPLACES LSTM MEMORY)
df["lag_1"] = df["consumption"].shift(1)
df["lag_2"] = df["consumption"].shift(2)
df["lag_3"] = df["consumption"].shift(3)

# 🔥 ROLLING FEATURES (TREND AWARENESS)
df["rolling_mean"] = df["consumption"].rolling(window=5).mean()
df["rolling_std"] = df["consumption"].rolling(window=5).std()

# Drop NaNs from lagging
df = df.dropna()

# =========================
# MODEL TRAINING
# =========================
features = [
    "time", "temperature",
    "time_squared", "sin_time", "cos_time",
    "lag_1", "lag_2", "lag_3",
    "rolling_mean", "rolling_std"
]

X = df[features]
y = df["consumption"]

model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X, y)

df["predicted"] = model.predict(X)

# =========================
# HIGH DEMAND ALERT SYSTEM
# =========================
threshold = df["consumption"].mean() + 2 * df["consumption"].std()
df["alert"] = df["predicted"] > threshold

# =========================
# DASHBOARD
# =========================
st.subheader("📊 Real vs Predicted (Time-Aware Model)")
st.line_chart(df[["consumption", "predicted"]])

st.subheader("🌡️ Temperature vs Consumption")
st.scatter_chart(df[["temperature", "consumption"]])

# =========================
# FUTURE FORECAST (SMART)
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

    new_df = pd.DataFrame([new_row])
    pred = model.predict(new_df)[0]

    future_predictions.append(pred)

    # update last_row for next step (simulate sequence)
    last_row["lag_2"] = last_row["lag_1"]
    last_row["lag_1"] = last_row["consumption"]
    last_row["consumption"] = pred
    last_row["time"] = new_time

future_df = pd.DataFrame({"predicted": future_predictions})

st.subheader("🔮 Future Forecast (Sequence-Aware)")
st.line_chart(future_df)

# =========================
# ALERTS
# =========================
st.subheader("🚨 High Demand Alerts")

alerts = df[df["alert"] == True]

if not alerts.empty:
    st.warning("⚠️ High Demand Detected!")
    st.dataframe(alerts)
else:
    st.success("✅ System Stable")

# =========================
# RAW DATA
# =========================
if st.checkbox("Show Raw Data"):
    st.dataframe(df)
