# stream_engine.py
import numpy as np
from config import BASE_DEMAND, NOISE_LEVEL

def generate_demand(t):
    noise = np.random.normal(0, NOISE_LEVEL)
    demand = BASE_DEMAND + (t * 0.5) + noise
    return round(demand, 2)