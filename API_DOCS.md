# Swim Metrics API Documentation

This API analyzes swimming sensor data to detect laps, strokes, and calculate kinematic metrics.

## Base URL

When running locally with Docker Compose: `http://localhost:8000`

## Endpoints

### `POST /metrics/session`

Analyzes a full session of sensor data.

#### Request Body

**Content-Type**: `application/json`

**Structure**:

```json
{
  "session_id": 123,       
  "swimmer_id": 1,         
  "exercise_id": 1,        
  "pool_length_m": 50.0,   
  "samples": [
    {
      "timestamp_ms": 1709424000000, 
      "accel_x": 0.02,
      "accel_y": 9.81,
      "accel_z": 0.15,
      "gyro_x": 0.01,
      "gyro_y": 0.00,
      "gyro_z": -0.01,
      "stroke_type": "Freestyle" 
    },
    ...
  ]
}
```

- `session_id`, `swimmer_id`, `exercise_id`: Optional identifiers passed back in the response.
- `pool_length_m`: Length of the pool in meters (default: 50.0).
- `samples`: List of sensor readings.
    - `timestamp_ms`: Unix timestamp in milliseconds.
    - `accel_*`: Accelerometer data (m/s²).
    - `gyro_*`: Gyroscope data (rad/s or deg/s, consistent with training data).
    - `stroke_type`: Optional pre-labeled stroke type.

#### Response Body

**Content-Type**: `application/json`

**Structure**:

```json
{
  "session_id": 123,
  "swimmer_id": 1,
  "exercise_id": 1,
  "session_averages": {
    "lap_count": 10,
    "stroke_count": 18.5,
    "avg_lap_time_s": 30.5,
    "avg_velocity_m_per_s": 1.64,
    "avg_stroke_rate_hz": 0.60,
    "avg_stroke_length_m": 2.75,
    "avg_stroke_index": 4.51
  },
  "laps": [
    {
      "lap_number": 1,
      "lap_time_s": 30.33,
      "stroke_count": 18,
      "velocity_m_per_s": 1.65,
      "stroke_rate_hz": 0.59,
      "stroke_rate_spm": 35.4,
      "stroke_length_m": 2.79,
      "stroke_index": 4.60,
      "stroke_type": "Freestyle"
    },
    ...
  ]
}
```

### `POST /metrics/upload_csv`

Analyzes data from a CSV file upload.

#### Request

**Content-Type**: `multipart/form-data`

**Body**: `file` (CSV file)

**CSV Format Requirements**:
- **Columns**: `unix_ts` (or `timestamp`), `accel_x`, `accel_y`, `accel_z`, `gyro_x`, `gyro_y`, `gyro_z`.
- **Optional**: `stroke_type`.
- **Timestamp**: Integer milliseconds.

#### Response

Same JSON structure as `/metrics/session`.

## Running the API

### With Docker Compose (Recommended)

1.  **Build and Start**:
    ```bash
    docker-compose up --build -d
    ```

2.  **Stop**:
    ```bash
    docker-compose down
    ```

### Without Docker

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Server**:
    ```bash
    uvicorn api:app --reload
    ```
