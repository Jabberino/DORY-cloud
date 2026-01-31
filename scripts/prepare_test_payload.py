import json

# Load raw samples from SQLite dump
with open("test_samples.json", "r") as f:
    raw_data = json.load(f)

# Transform to API format
samples = []
for row in raw_data:
    # Handle timestamp: use unix_ts if available, else timestamp
    ts = row.get("unix_ts") or row.get("timestamp")
    
    samples.append({
        "timestamp_ms": ts,
        "accel_x": row["accel_x"],
        "accel_y": row["accel_y"],
        "accel_z": row["accel_z"],
        "gyro_x": row["gyro_x"],
        "gyro_y": row["gyro_y"],
        "gyro_z": row["gyro_z"],
        "stroke_type": row.get("stroke_type")
    })

payload = {
    "session_id": 123,
    "swimmer_id": 1,
    "exercise_id": 1,
    "pool_length_m": 50.0,
    "samples": samples
}

with open("test_payload.json", "w") as f:
    json.dump(payload, f, indent=2)

print(f"Created test_payload.json with {len(samples)} samples.")
