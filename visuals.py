# visuals.py
import pandas as pd

def build_chart(time, data):
    df = pd.DataFrame({
        "Time": time,
        "Demand": data
    })
    return df