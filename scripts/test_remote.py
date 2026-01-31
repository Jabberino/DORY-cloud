import requests
import json
import pandas as pd
import os

# Configuration provided by user
HOST = "ccscloud.dlsu.edu.ph"
PORT = "11526"
# Attempting HTTP first as "http port" was specified, despite "https" in the URL text
BASE_URL = f"http://{HOST}:{PORT}"
ENDPOINT = "/metrics/upload_csv"
URL = f"{BASE_URL}{ENDPOINT}"

CSV_FILE = "test_data.csv"
SOURCE_JSON = "test_samples.json"

def create_test_csv():
    if not os.path.exists(SOURCE_JSON):
        print(f"Error: {SOURCE_JSON} not found. Cannot generate test CSV.")
        return False
        
    try:
        with open(SOURCE_JSON, "r") as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        # Ensure timestamp column availability
        if "unix_ts" not in df.columns and "timestamp" in df.columns:
            df["unix_ts"] = df["timestamp"]
            
        cols = ["unix_ts", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
        if "stroke_type" in df.columns:
            cols.append("stroke_type")
            
        df = df[cols]
        df.to_csv(CSV_FILE, index=False)
        print(f"Generated {CSV_FILE} with {len(df)} rows.")
        return True
    except Exception as e:
        print(f"Failed to generate CSV: {e}")
        return False

def test_remote():
    if not os.path.exists(CSV_FILE):
        print(f"{CSV_FILE} not found. Attempting to generate...")
        if not create_test_csv():
            return

    print(f"Testing Remote URL: {URL}")
    print(f"Uploading {CSV_FILE}...")
    
    try:
        with open(CSV_FILE, "rb") as f:
            files = {"file": f}
            # Set timeout to avoid hanging if the server is unreachable
            response = requests.post(URL, files=files, timeout=10)
            
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS! API responded with metrics.")
            data = response.json()
            print("\nSession Averages:")
            print(json.dumps(data.get("session_averages"), indent=2))
            print(f"\nTotal Laps Detected: {len(data.get('laps', []))}")
        else:
            print("FAILURE. Server returned error:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"\nConnection Error: Could not connect to {URL}.")
        print("Please check: 1. The URL/Port are correct. 2. The server is up. 3. Firewall/VPN settings.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    test_remote()
