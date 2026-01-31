import requests

# Ensure verify_api.sh has run or Docker is up
URL = "http://localhost:8000/metrics/upload_csv"
CSV_FILE = "test_data.csv"

# Create a dummy CSV file if it doesn't exist (using the json data we had)
import json
import pandas as pd

try:
    with open("test_samples.json", "r") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    # Ensure columns match expectations
    if "unix_ts" not in df.columns and "timestamp" in df.columns:
        df["unix_ts"] = df["timestamp"]
        
    df = df[["unix_ts", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z", "stroke_type"]]
    df.to_csv(CSV_FILE, index=False)
    print(f"Created {CSV_FILE}")
except Exception as e:
    print(f"Could not create test CSV from test_samples.json: {e}")
    exit(1)

print(f"Uploading {CSV_FILE} to {URL}...")
with open(CSV_FILE, "rb") as f:
    files = {"file": f}
    response = requests.post(URL, files=files)

print("Status Code:", response.status_code)
if response.status_code == 200:
    print("Response Support Summary:")
    print(json.dumps(response.json()["session_averages"], indent=2))
else:
    print("Error:", response.text)
