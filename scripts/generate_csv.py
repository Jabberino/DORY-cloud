import json
import csv
import os

SOURCE_JSON = "test_samples.json"
CSV_FILE = "test_data.csv"

def generate_csv():
    if not os.path.exists(SOURCE_JSON):
        print(f"Error: {SOURCE_JSON} not found.")
        return

    with open(SOURCE_JSON, "r") as f:
        data = json.load(f)

    if not data:
        print("Error: No data in JSON.")
        return

    # Determine headers
    # We need specific columns for the API
    headers = ["unix_ts", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z", "stroke_type"]
    
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for row in data:
            # Map timestamp -> unix_ts if needed
            ts = row.get("unix_ts") or row.get("timestamp")
            
            # Construct row
            out_row = {
                "unix_ts": ts,
                "accel_x": row.get("accel_x"),
                "accel_y": row.get("accel_y"),
                "accel_z": row.get("accel_z"),
                "gyro_x": row.get("gyro_x"),
                "gyro_y": row.get("gyro_y"),
                "gyro_z": row.get("gyro_z"),
                "stroke_type": row.get("stroke_type")
            }
            writer.writerow(out_row)
            
    print(f"Successfully generated {CSV_FILE} with {len(data)} rows.")

if __name__ == "__main__":
    generate_csv()
