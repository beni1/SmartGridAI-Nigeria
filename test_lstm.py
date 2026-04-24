import numpy as np
from lstm_model import train_lstm, predict_next

# Fake time-series data
data = np.linspace(100, 200, 100)

print("Training LSTM...")
model = train_lstm(data)

# Take last 10 points
last_window = data[-10:]

prediction = predict_next(model, last_window)

print("Last value:", last_window[-1])
print("Predicted next value:", prediction)
