import numpy as np

def detect_anomalies(values, threshold=1.5):
    values = np.array(values, dtype=float)

    mean = np.mean(values)
    std = np.std(values)

    if std == 0:
        return []

    z_scores = (values - mean) / std

    anomalies = []
    for i, z in enumerate(z_scores):
        if abs(z) > threshold:
            anomalies.append({
                "index": i,
                "value": values[i],
                "z_score": float(z)
            })

    return anomalies
