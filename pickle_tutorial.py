import joblib
import pandas as pd
import os

print("--- PICKLE FILE CONNECTION TUTORIAL ---")

# 1. Path to your pickle model file
pickle_path = "house_data.joblib"

if not os.path.exists(pickle_path):
    print(f"File {pickle_path} not found!")
    exit(1)

print(f"1. Connecting to Pickle/Joblib model file: {pickle_path}")

# 2. LOAD / DESERIALIZE THE PICKLE FILE
loaded_data = joblib.load(pickle_path)
print(f"2. File successfully loaded into memory! Type: {type(loaded_data)}")

if isinstance(loaded_data, pd.DataFrame):
    print("\n--- DATA PREVIEW ---")
    print(loaded_data.head())
else:
    # Sample input matching standard columns
    sample_input = pd.DataFrame([{
        "LotArea": 9500,
        "OverallQual": 8,
        "OverallCond": 6,
        "YearBuilt": 2018,
        "GrLivArea": 2100,
        "GarageCars": 2
    }])
    prediction = loaded_data.predict(sample_input)
    print(f"Predicted Price: ${prediction[0]:,.2f}")
