import pandas as pd

# Sample data
features_dict = {
    "urlLength": [22],
    "urlDepth": [-1],
    "protocol": ["https"],
    "domain": ["www.google.com"],
    "domainAge": [9807],
    "registrar": ["MarkMonitor, Inc."],
    "sslAge": [27],
    "PageRank": [3]
}

# Convert to DataFrame
df = pd.DataFrame(features_dict)

# Load your model here
import dill
model_path = 'Model.pkl'
with open(model_path, 'rb') as file:
    model = dill.load(file)

# Make prediction
prediction = model.predict_proba(df)
print("Prediction:", prediction)
