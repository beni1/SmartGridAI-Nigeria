import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


def prepare_data(series, window_size=10):
    X, y = [], []

    for i in range(len(series) - window_size):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size])

    return np.array(X), np.array(y)


def build_lstm_model(input_shape):
    model = Sequential()

    model.add(LSTM(50, activation='relu', input_shape=input_shape))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mse')

    return model


def train_lstm(series):
    X, y = prepare_data(series)

    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = build_lstm_model((X.shape[1], 1))

    model.fit(X, y, epochs=5, verbose=1)

    return model


def predict_next(model, last_window):
    last_window = np.array(last_window).reshape((1, len(last_window), 1))
    prediction = model.predict(last_window, verbose=0)
    return float(prediction[0][0])
