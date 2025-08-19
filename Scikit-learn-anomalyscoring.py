from sklearn.ensemble import IsolationForest
import numpy as np

# Sample data: rows of [burn_amount, proposal_success_rate, event_freq]
data = np.array([
    [100, 0.9, 5],
    [120, 0.85, 6],
    [5000, 0.1, 20],  # anomaly candidate
    [110, 0.88, 4],
])

model = IsolationForest(contamination=0.1)
model.fit(data)

# New event
new_event = np.array([[4500, 0.2, 18]])
score = model.decision_function(new_event)  # negative = anomaly
is_anomaly = model.predict(new_event) == -1
print(f"Anomaly detected: {is_anomaly} with score {score}")
