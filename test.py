import numpy as np
from sklearn.linear_model import LinearRegression


def predict_next_elements(sequence, n_predictions=4):
    # Ensure input is a 1D numpy array
    sequence = np.array(sequence).flatten()
    n = len(sequence)

    # Prepare training data: X as indices, y as values
    X = np.arange(n).reshape(-1, 1)
    y = sequence

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next `n_predictions` values
    next_indices = np.arange(n, n + n_predictions).reshape(-1, 1)
    predictions = model.predict(next_indices)

    return predictions.tolist()


# Example usage
sequence = [1,10,100,1000,10000]  # Dynamic size
predicted_values = predict_next_elements(sequence)
print("Predicted next 4 values:", predicted_values)
