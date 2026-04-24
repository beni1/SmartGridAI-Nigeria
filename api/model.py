import numpy as np

def generate_demand(n_points=200):
    np.random.seed(42)

    time = np.arange(1, n_points + 1)

    # Simulated temperature pattern (daily cycle + randomness)
    temperature = 28 + 5 * np.sin(time / 15) + np.random.normal(0, 1, 
n_points)

    # Base consumption trend
    base = 100 + (time * 0.3)

    # Demand influenced by temperature (hotter → more usage)
    demand = base + (temperature * 2)

    # Add random fluctuations (grid instability simulation)
    noise = np.random.normal(0, 5, n_points)

    consumption = demand + noise

    return {
        "time": time.tolist(),
        "temperature": temperature.tolist(),
        "consumption": consumption.tolist()
    }
