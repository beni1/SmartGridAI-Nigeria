import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/demand"
API_KEY = "smartgrid-secret-key"

st.set_page_config(page_title="SmartGridAI", layout="wide")
st.title("⚡ SmartGridAI Dashboard (API Mode)")

if st.button("Generate Demand Data"):
    try:
        response = requests.get(
            API_URL,
            headers={"x-api-key": API_KEY}
        )

        if response.status_code == 200:
            data = response.json()

            st.subheader("Energy Consumption")
            st.line_chart(data["consumption"])

            st.subheader("Temperature")
            st.line_chart(data["temperature"])

        else:
            st.error("Unauthorized or API error")

    except Exception as e:
        st.error(f"Connection failed: {e}")
