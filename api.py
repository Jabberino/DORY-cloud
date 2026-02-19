from typing import List, Optional
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd

from lap_stroke_pipeline import run_pipeline_from_df, BoutConfig, LapConfig


app = FastAPI(title="Swim Metrics API", version="0.2.0")


class Sample(BaseModel):
    timestamp_ms: int
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    stroke_type: Optional[str] = None


class BoutConfigIn(BaseModel):
    """Configuration for swimming bout detection (acceleration-based)."""
    accel_threshold: float = 12.0
    gap_fill_seconds: float = 7.0
    bout_filter_seconds: float = 30.0


class LapConfigIn(BaseModel):
    """Configuration for lap turn detection (gyroscope-based)."""
    window_size_seconds: int = 1
    cutoff_frequency_hz: float = 3.0
    lap_turn_threshold: float = 1.2
    boundary_buffer_seconds: int = 35
    debounce_seconds: int = 35


class SessionRequest(BaseModel):
    session_id: Optional[int] = None
    swimmer_id: Optional[int] = None
    exercise_id: Optional[int] = None
    pool_length_m: float = 50.0
    bout_config: Optional[BoutConfigIn] = None
    lap_config: Optional[LapConfigIn] = None
    samples: List[Sample]


class LapOut(BaseModel):
    lap_number: int
    lap_time_s: float
    stroke_count: int
    velocity_m_per_s: float
    stroke_rate_hz: float
    stroke_rate_spm: float
    stroke_length_m: float
    stroke_index: float
    stroke_type: Optional[str] = None


class SessionAveragesOut(BaseModel):
    lap_count: int
    stroke_count: float
    avg_lap_time_s: float
    avg_velocity_m_per_s: float
    avg_stroke_rate_hz: float
    avg_stroke_length_m: float
    avg_stroke_index: float


class MetricsResponse(BaseModel):
    session_id: Optional[int] = None
    swimmer_id: Optional[int] = None
    exercise_id: Optional[int] = None
    session_averages: SessionAveragesOut
    laps: List[LapOut]


def _format_response(
    per_lap_results: List[dict],
    session_averages: dict,
    session_id: Optional[int] = None,
    swimmer_id: Optional[int] = None,
    exercise_id: Optional[int] = None
) -> MetricsResponse:
    laps = [
        LapOut(
            lap_number=int(lap["lap_number"]),
            lap_time_s=float(lap["lap_time"]),
            stroke_count=int(lap["stroke_count"]),
            velocity_m_per_s=float(lap["velocity"]),
            stroke_rate_hz=float(lap["stroke_rate_s"]),
            stroke_rate_spm=float(lap["stroke_rate_min"]),
            stroke_length_m=float(lap["stroke_length"]),
            stroke_index=float(lap["stroke_index"]),
            stroke_type=lap.get("stroke_type"),
        )
        for lap in per_lap_results
    ]

    avg = SessionAveragesOut(
        lap_count=len(laps),
        stroke_count=float(session_averages.get("avg_stroke_count", 0.0)),
        avg_lap_time_s=float(session_averages.get("avg_lap_time", 0.0)),
        avg_velocity_m_per_s=float(session_averages.get("avg_velocity", 0.0)),
        avg_stroke_rate_hz=float(session_averages.get("avg_stroke_rate", 0.0)),
        avg_stroke_length_m=float(session_averages.get("avg_stroke_length", 0.0)),
        avg_stroke_index=float(session_averages.get("avg_stroke_index", 0.0)),
    )

    return MetricsResponse(
        session_id=session_id,
        swimmer_id=swimmer_id,
        exercise_id=exercise_id,
        session_averages=avg,
        laps=laps,
    )


def _build_dataframe_from_request(req: SessionRequest) -> pd.DataFrame:
    data = [
        {
            "timestamp": s.timestamp_ms,
            "unix_ts": s.timestamp_ms,
            "accel_x": s.accel_x,
            "accel_y": s.accel_y,
            "accel_z": s.accel_z,
            "gyro_x": s.gyro_x,
            "gyro_y": s.gyro_y,
            "gyro_z": s.gyro_z,
            "stroke_type": s.stroke_type,
        }
        for s in req.samples
    ]
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("Asia/Manila")
    return df


@app.post("/metrics/session", response_model=MetricsResponse)
def compute_metrics(req: SessionRequest) -> MetricsResponse:
    if not req.samples:
        return _format_response([], {}, req.session_id, req.swimmer_id, req.exercise_id)

    df = _build_dataframe_from_request(req)

    bout_cfg = BoutConfig(**req.bout_config.model_dump()) if req.bout_config else BoutConfig()
    lap_cfg = LapConfig(**req.lap_config.model_dump()) if req.lap_config else LapConfig()

    per_lap_results, session_averages = run_pipeline_from_df(df, bout_config=bout_cfg, lap_config=lap_cfg)
    return _format_response(per_lap_results, session_averages, req.session_id, req.swimmer_id, req.exercise_id)


@app.post("/metrics/upload_csv", response_model=MetricsResponse)
async def upload_csv(file: UploadFile = File(...)) -> MetricsResponse:
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")

    # Normalize timestamp column
    if "unix_ts" in df.columns:
        df["timestamp"] = df["unix_ts"]
    elif "timestamp" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must have 'unix_ts' or 'timestamp' column")

    # Add datetime column if missing (run_pipeline_from_df needs it mostly, via subcalls?)
    # Actually run_pipeline_from_df expects 'datetime' column or creates it?
    # No, run_pipeline_from_df calls add_is_swimming etc.
    # But wait, run_pipeline_from_df calls `estimate_sampling_interval_seconds` which needs `datetime`
    # We must ensure `datetime` is present.
    
    if "datetime" not in df.columns:
        # Assuming ms timestamp if it's int-like, but let's conform to other loaders
        try:
             df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("Asia/Manila")
        except Exception:
             raise HTTPException(status_code=400, detail="Could not parse timestamp column as milliseconds")

    # Validate required columns
    required_cols = ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    per_lap_results, session_averages = run_pipeline_from_df(df)

    # Can't easily extract IDs from CSV unless defined in header/filename convention
    # Returning None for IDs
    return _format_response(per_lap_results, session_averages)
