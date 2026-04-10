import pandas as pd
import numpy as np
import streamlit as st

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

st.title("⚡ SmartGridAI - Hybrid ML + DL Dashboard")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/demand_large.csv")

# =========================
# FEATURE ENGINEERING (RF MODEL)
# =========================
df["time_squared"] = df["time"] ** 2
df["sin_time"] = np.sin(df["time"] / 10)
df["cos_time"] = np.cos(df["time"] / 10)

X_rf = df[["time", "temperature", "time_squared", "sin_time", "cos_time"]]
y = df["consumption"]

# =========================
# RANDOM FOREST MODEL
# =========================
rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
rf_model.fit(X_rf, y)

df["rf_predicted"] = rf_model.predict(X_rf)

# =========================
# =========================
# LSTM MODEL (DEEP LEARNING)
# =========================
# =========================

sequence_length = 24

scaler = MinMaxScaler()
consumption_scaled = scaler.fit_transform(df[["consumption"]])

X_lstm = []
y_lstm = []

for i in range(sequence_length, len(consumption_scaled)):
    X_lstm.append(consumption_scaled[i-sequence_length:i])
    y_lstm.append(consumption_scaled[i])

X_lstm = np.array(X_lstm)
y_lstm = np.array(y_lstm)

X_lstm = X_lstm.reshape((X_lstm.shape[0], X_lstm.shape[1], 1))

model = Sequential()
model.add(LSTM(50, return_sequences=False, input_shape=(sequence_length, 1)))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mse')
model.fit(X_lstm, y_lstm, epochs=3, batch_size=32, verbose=0)

# Predictions (LSTM)
lstm_pred = model.predict(X_lstm)
lstm_pred = scaler.inverse_transform(lstm_pred)

# Align size with dataframe
df_lstm = df.iloc[sequence_length:].copy()
df_lstm["lstm_predicted"] = lstm_pred

# =========================
# HIGH DEMAND ALERT SYSTEM
# =========================
threshold = df["consumption"].mean() + 2 * df["consumption"].std()

df_lstm["alert"] = df_lstm["lstm_predicted"] > threshold

# =========================
# STREAMLIT DASHBOARD
# =========================

st.subheader("📊 RandomForest: Real vs Predicted")
st.line_chart(df[["consumption", "rf_predicted"]])

st.subheader("🧠 LSTM: Real vs Predicted")
st.line_chart(df_lstm[["lstm_predicted"]])

st.subheader("🌡️ Temperature vs Consumption")
st.scatter_chart(df[["temperature", "consumption"]])

# =========================
# FUTURE FORECAST (RF)
# =========================
future_time = np.arange(df["time"].max() + 1, df["time"].max() + 21)
future_temp = 28 + 5 * np.sin(future_time / 50)

future_df = pd.DataFrame({
    "time": future_time,
    "temperature": future_temp
})

future_df["time_squared"] = future_df["time"] ** 2
future_df["sin_time"] = np.sin(future_df["time"] / 10)
future_df["cos_time"] = np.cos(future_df["time"] / 10)

future_df["predicted"] = rf_model.predict(
    future_df[["time", "temperature", "time_squared", "sin_time", "cos_time"]]
)

st.subheader("🔮 Future Demand Forecast (RF)")
st.line_chart(future_df[["predicted"]])

# =========================
# ALERTS
# =========================
st.subheader("🚨 High Demand Alerts (LSTM-based)")

alerts = df_lstm[df_lstm["alert"] == True]

if not alerts.empty:
    st.warning("⚠️ High Demand Detected!")
    st.dataframe(alerts)
else:
    st.success("✅ No critical demand spikes detected")

# =========================
# RAW DATA
# =========================
show_data = st.checkbox("Show Raw Data")

if show_data:
    st.dataframe(df)
