import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LinearRegression

st.title("⚡ SmartGridAI - Energy Demand Dashboard")

# Load data
df = pd.read_csv("data/demand_large.csv")

# =========================
# STEP 1: Train Model
# =========================
X = df[["time", "temperature"]]
y = df["consumption"]

model = LinearRegression()
model.fit(X, y)

# Predictions
df["predicted"] = model.predict(X)

# =========================
# STEP 2: Real vs Predicted
# =========================
st.subheader("📊 Real vs Predicted Consumption")
st.line_chart(df[["consumption", "predicted"]])

# =========================
# STEP 3: Temperature Effect
# =========================
st.subheader("🌡️ Temperature vs Consumption")
st.scatter_chart(df[["temperature", "consumption"]])

# =========================
# STEP 4: Future Forecast
# =========================
future_time = np.arange(df["time"].max() + 1, df["time"].max() + 21)
future_temp = 28 + 5 * np.sin(future_time / 50)

future_df = pd.DataFrame({
    "time": future_time,
    "temperature": future_temp
})

future_df["predicted"] = model.predict(future_df)

st.subheader("🔮 Future Demand Forecast")
st.line_chart(future_df[["predicted"]])

# =========================
# Extra: Show raw data
# =========================
show_data = st.checkbox("Show Raw Data")

if show_data:
    st.write(df)

st.write(df.shape)
