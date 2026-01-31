"""Pydantic schemas for API request/response validation."""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from .models import Sex, ExerciseCategory, GoalType, StrokeType


# ---------------------------------------------------------------------------
# Base schemas (shared fields)
# ---------------------------------------------------------------------------

class TimestampMixin(BaseModel):
    created_at: datetime


# ---------------------------------------------------------------------------
# Team schemas
# ---------------------------------------------------------------------------

class TeamCreate(BaseModel):
    name: str = Field(..., max_length=100)


class TeamResponse(TimestampMixin):
    id: UUID
    name: str
    join_code: str

    class Config:
        from_attributes = True


class TeamWithMembers(TeamResponse):
    coaches: List["CoachBrief"] = []
    swimmers: List["SwimmerBrief"] = []


# ---------------------------------------------------------------------------
# Coach schemas
# ---------------------------------------------------------------------------

class CoachCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr


class CoachResponse(TimestampMixin):
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True


class CoachBrief(BaseModel):
    id: UUID
    name: str
    email: str
    is_owner: bool = False

    class Config:
        from_attributes = True


class AddCoachToTeam(BaseModel):
    coach_id: UUID
    is_owner: bool = False


# ---------------------------------------------------------------------------
# Swimmer schemas
# ---------------------------------------------------------------------------

class SwimmerCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: Optional[EmailStr] = None
    birthday: date
    sex: Sex
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    wingspan_cm: float = Field(..., gt=0)


class SwimmerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None
    sex: Optional[Sex] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    wingspan_cm: Optional[float] = Field(None, gt=0)


class SwimmerResponse(TimestampMixin):
    id: UUID
    name: str
    email: Optional[str]
    birthday: date
    sex: Sex
    height_cm: float
    weight_kg: float
    wingspan_cm: float

    class Config:
        from_attributes = True


class SwimmerBrief(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class AddSwimmerToTeam(BaseModel):
    swimmer_id: UUID


# ---------------------------------------------------------------------------
# Exercise schemas
# ---------------------------------------------------------------------------

class ExerciseCreate(BaseModel):
    name: str = Field(..., max_length=100)
    category: ExerciseCategory
    distance_m: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None


class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[ExerciseCategory] = None
    distance_m: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None


class ExerciseResponse(TimestampMixin):
    id: UUID
    team_id: Optional[UUID]
    name: str
    category: ExerciseCategory
    distance_m: Optional[int]
    description: Optional[str]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Session schemas
# ---------------------------------------------------------------------------

class SensorSampleCreate(BaseModel):
    timestamp: int  # Unix ms
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    heart_rate: Optional[float] = None
    ppg: Optional[float] = None
    ecg: Optional[float] = None


class SessionCreate(BaseModel):
    swimmer_id: UUID
    exercise_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    pool_length_m: int = 50
    notes: Optional[str] = None
    samples: List[SensorSampleCreate] = []


class LapResultResponse(BaseModel):
    id: UUID
    lap_number: int
    lap_time_s: float
    stroke_count: int
    stroke_type: Optional[StrokeType]
    velocity_m_s: Optional[float]
    stroke_rate_hz: Optional[float]
    stroke_length_m: Optional[float]
    stroke_index: Optional[float]

    class Config:
        from_attributes = True


class SessionResultResponse(BaseModel):
    id: UUID
    lap_count: int
    total_stroke_count: int
    avg_lap_time_s: Optional[float]
    avg_velocity_m_s: Optional[float]
    avg_stroke_rate_hz: Optional[float]
    avg_stroke_length_m: Optional[float]
    avg_stroke_index: Optional[float]
    stroke_distribution: Optional[dict]
    computed_at: datetime
    laps: List[LapResultResponse] = []

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: UUID
    swimmer_id: UUID
    exercise_id: Optional[UUID]
    team_id: Optional[UUID]
    started_at: datetime
    ended_at: Optional[datetime]
    pool_length_m: int
    notes: Optional[str]
    result: Optional[SessionResultResponse] = None

    class Config:
        from_attributes = True


class SessionBrief(BaseModel):
    id: UUID
    started_at: datetime
    ended_at: Optional[datetime]
    pool_length_m: int
    has_results: bool = False

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Goal schemas
# ---------------------------------------------------------------------------

class GoalCreate(BaseModel):
    event_name: str = Field(..., max_length=100)
    target_time_s: float = Field(..., gt=0)
    goal_type: GoalType
    start_date: date
    end_date: date


class GoalUpdate(BaseModel):
    event_name: Optional[str] = Field(None, max_length=100)
    target_time_s: Optional[float] = Field(None, gt=0)
    goal_type: Optional[GoalType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class GoalProgressCreate(BaseModel):
    session_id: Optional[UUID] = None
    projected_time_s: float = Field(..., gt=0)


class GoalProgressResponse(BaseModel):
    id: UUID
    goal_id: UUID
    session_id: Optional[UUID]
    recorded_at: datetime
    projected_time_s: float

    class Config:
        from_attributes = True


class GoalResponse(TimestampMixin):
    id: UUID
    swimmer_id: UUID
    event_name: str
    target_time_s: float
    goal_type: GoalType
    start_date: date
    end_date: date
    is_active: bool

    class Config:
        from_attributes = True


class GoalWithProgress(GoalResponse):
    progress: List[GoalProgressResponse] = []


# ---------------------------------------------------------------------------
# Forward reference updates
# ---------------------------------------------------------------------------

TeamWithMembers.model_rebuild()
