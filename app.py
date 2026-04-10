import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

st.title("⚡ SmartGridAI - Energy Demand Dashboard")

# Load data
df = pd.read_csv("data/demand_large.csv")

# =========================
# STEP 1: Feature Engineering (REAL FIX)
# =========================
df["time_squared"] = df["time"] ** 2
df["sin_time"] = np.sin(df["time"] / 10)
df["cos_time"] = np.cos(df["time"] / 10)

# =========================
# STEP 2: Train Model
# =========================
X = df[["time", "temperature", "time_squared", "sin_time", "cos_time"]]
y = df["consumption"]

model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X, y)

# Predictions
df["predicted"] = model.predict(X)

# =========================
# STEP 3: Real vs Predicted
# =========================
st.subheader("📊 Real vs Predicted Consumption")
st.line_chart(df[["consumption", "predicted"]])

# =========================
# STEP 4: Temperature Effect
# =========================
st.subheader("🌡️ Temperature vs Consumption")
st.scatter_chart(df[["temperature", "consumption"]])

# =========================
# STEP 5: Future Forecast (UPDATED)
# =========================
future_time = np.arange(df["time"].max() + 1, df["time"].max() + 21)
future_temp = 28 + 5 * np.sin(future_time / 50)

future_df = pd.DataFrame({
    "time": future_time,
    "temperature": future_temp
})

# IMPORTANT: same features as training
future_df["time_squared"] = future_df["time"] ** 2
future_df["sin_time"] = np.sin(future_df["time"] / 10)
future_df["cos_time"] = np.cos(future_df["time"] / 10)

future_df["predicted"] = model.predict(
    future_df[["time", "temperature", "time_squared", "sin_time", "cos_time"]]
)

st.subheader("🔮 Future Demand Forecast")
st.line_chart(future_df[["predicted"]])

# =========================
# Extra: Show raw data
# =========================
show_data = st.checkbox("Show Raw Data")

if show_data:
    st.dataframe(df)

