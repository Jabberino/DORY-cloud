"""Sessions router with ML pipeline integration."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd

from ..database import get_db
from ..models import SwimSession, SensorSample, SessionResult, LapResult, Swimmer
from ..schemas import SessionCreate, SessionResponse, SessionBrief, ProcessSessionRequest

# Import the existing ML pipeline
import sys
sys.path.insert(0, '..')
from lap_stroke_pipeline import run_pipeline_from_df, BoutConfig, LapConfig

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """Create a new swim session with sensor samples."""
    # Validate swimmer exists
    swimmer = db.query(Swimmer).filter(Swimmer.id == session_data.swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    # Create session
    session = SwimSession(
        swimmer_id=session_data.swimmer_id,
        exercise_id=session_data.exercise_id,
        team_id=session_data.team_id,
        started_at=session_data.started_at,
        ended_at=session_data.ended_at,
        pool_length_m=session_data.pool_length_m,
        notes=session_data.notes
    )
    db.add(session)
    db.flush()  # Get session ID
    
    # Add sensor samples
    for sample in session_data.samples:
        sensor = SensorSample(
            session_id=session.id,
            timestamp=sample.timestamp,
            accel_x=sample.accel_x,
            accel_y=sample.accel_y,
            accel_z=sample.accel_z,
            gyro_x=sample.gyro_x,
            gyro_y=sample.gyro_y,
            gyro_z=sample.gyro_z,
            heart_rate=sample.heart_rate,
            ppg=sample.ppg,
            ecg=sample.ecg
        )
        db.add(sensor)
    
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """Get session with results."""
    session = db.query(SwimSession).filter(SwimSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("", response_model=List[SessionBrief])
def list_sessions_for_swimmer(swimmer_id: UUID, db: Session = Depends(get_db)):
    """List sessions for a swimmer."""
    sessions = db.query(SwimSession).filter(SwimSession.swimmer_id == swimmer_id).all()
    return [
        SessionBrief(
            id=s.id,
            started_at=s.started_at,
            ended_at=s.ended_at,
            pool_length_m=s.pool_length_m,
            has_results=s.result is not None
        )
        for s in sessions
    ]


@router.post("/{session_id}/process", response_model=SessionResponse)
def process_session(
    session_id: UUID,
    cfg: Optional[ProcessSessionRequest] = None,
    db: Session = Depends(get_db),
):
    """Run ML pipeline on session sensor data."""
    session = db.query(SwimSession).filter(SwimSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if already processed
    if session.result:
        raise HTTPException(status_code=400, detail="Session already processed")
    
    # Get sensor samples
    samples = db.query(SensorSample).filter(SensorSample.session_id == session_id).order_by(SensorSample.timestamp).all()
    if not samples:
        raise HTTPException(status_code=400, detail="No sensor data for session")
    
    # Build DataFrame for pipeline
    df = pd.DataFrame([{
        'timestamp': s.timestamp,
        'accel_x': s.accel_x,
        'accel_y': s.accel_y,
        'accel_z': s.accel_z,
        'gyro_x': s.gyro_x,
        'gyro_y': s.gyro_y,
        'gyro_z': s.gyro_z,
    } for s in samples])
    
    # Add datetime column (required by pipeline)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert('Asia/Manila')
    
    # Build pipeline configs (use defaults when not provided)
    bout_cfg = BoutConfig(**(cfg.bout_config.model_dump() if cfg and cfg.bout_config else {}))
    lap_cfg = LapConfig(**(cfg.lap_config.model_dump() if cfg and cfg.lap_config else {}))

    # Run ML pipeline
    try:
        per_lap_results, session_averages = run_pipeline_from_df(df, bout_config=bout_cfg, lap_config=lap_cfg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    
    # Store results
    result = SessionResult(
        session_id=session_id,
        lap_count=len(per_lap_results),
        total_stroke_count=sum(lap.get('stroke_count', 0) for lap in per_lap_results),
        avg_lap_time_s=session_averages.get('avg_lap_time'),
        avg_velocity_m_s=session_averages.get('avg_velocity'),
        avg_stroke_rate_hz=session_averages.get('avg_stroke_rate'),
        avg_stroke_length_m=session_averages.get('avg_stroke_length'),
        avg_stroke_index=session_averages.get('avg_stroke_index'),
        stroke_distribution=None,  # TODO: compute from lap stroke types
        computed_at=datetime.utcnow()
    )
    db.add(result)
    db.flush()
    
    # Store per-lap results
    for lap in per_lap_results:
        lap_result = LapResult(
            session_result_id=result.id,
            lap_number=lap['lap_number'],
            lap_time_s=lap['lap_time'],
            stroke_count=lap['stroke_count'],
            stroke_type=lap.get('stroke_type'),
            velocity_m_s=lap['velocity'],
            stroke_rate_hz=lap['stroke_rate_s'],
            stroke_length_m=lap['stroke_length'],
            stroke_index=lap['stroke_index']
        )
        db.add(lap_result)
    
    db.commit()
    db.refresh(session)
    return session
