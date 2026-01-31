"""SQLAlchemy models for the swim pipeline database."""

import uuid
from datetime import datetime, date
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Float, Integer, BigInteger, Boolean, Date, DateTime,
    ForeignKey, Text, Enum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Sex(str, PyEnum):
    M = "M"
    F = "F"


class ExerciseCategory(str, PyEnum):
    SPRINT = "sprint"
    DISTANCE = "distance"


class GoalType(str, PyEnum):
    SPRINT = "sprint"
    ENDURANCE = "endurance"


class StrokeType(str, PyEnum):
    FREESTYLE = "freestyle"
    BACKSTROKE = "backstroke"
    BREASTSTROKE = "breaststroke"
    BUTTERFLY = "butterfly"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Team(Base):
    """Team entity."""
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    join_code = Column(String(8), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    coaches = relationship("TeamCoach", back_populates="team", cascade="all, delete-orphan")
    swimmers = relationship("TeamSwimmer", back_populates="team", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="team", cascade="all, delete-orphan")
    sessions = relationship("SwimSession", back_populates="team")


class Coach(Base):
    """Coach entity."""
    __tablename__ = "coaches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    teams = relationship("TeamCoach", back_populates="coach", cascade="all, delete-orphan")


class Swimmer(Base):
    """Swimmer entity with physical profile."""
    __tablename__ = "swimmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    birthday = Column(Date, nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    wingspan_cm = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    teams = relationship("TeamSwimmer", back_populates="swimmer", cascade="all, delete-orphan")
    sessions = relationship("SwimSession", back_populates="swimmer")
    goals = relationship("Goal", back_populates="swimmer", cascade="all, delete-orphan")


class TeamCoach(Base):
    """Junction table: Team <-> Coach."""
    __tablename__ = "team_coaches"
    __table_args__ = (
        UniqueConstraint("team_id", "coach_id", name="uq_team_coach"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.id", ondelete="CASCADE"), nullable=False)
    is_owner = Column(Boolean, default=False, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    team = relationship("Team", back_populates="coaches")
    coach = relationship("Coach", back_populates="teams")


class TeamSwimmer(Base):
    """Junction table: Team <-> Swimmer."""
    __tablename__ = "team_swimmers"
    __table_args__ = (
        UniqueConstraint("team_id", "swimmer_id", name="uq_team_swimmer"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    swimmer_id = Column(UUID(as_uuid=True), ForeignKey("swimmers.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    team = relationship("Team", back_populates="swimmers")
    swimmer = relationship("Swimmer", back_populates="teams")


class Exercise(Base):
    """Exercise template belonging to a team."""
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum(ExerciseCategory), nullable=False)
    distance_m = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    team = relationship("Team", back_populates="exercises")
    sessions = relationship("SwimSession", back_populates="exercise")


class SwimSession(Base):
    """A swim training session."""
    __tablename__ = "swim_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    swimmer_id = Column(UUID(as_uuid=True), ForeignKey("swimmers.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    pool_length_m = Column(Integer, default=50, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    swimmer = relationship("Swimmer", back_populates="sessions")
    exercise = relationship("Exercise", back_populates="sessions")
    team = relationship("Team", back_populates="sessions")
    sensor_samples = relationship("SensorSample", back_populates="session", cascade="all, delete-orphan")
    result = relationship("SessionResult", back_populates="session", uselist=False, cascade="all, delete-orphan")


class SensorSample(Base):
    """Raw sensor data sample from wearable device."""
    __tablename__ = "sensor_samples"
    __table_args__ = (
        Index("ix_sensor_samples_session_id", "session_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("swim_sessions.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(BigInteger, nullable=False)  # Unix milliseconds

    # Accelerometer
    accel_x = Column(Float, nullable=True)
    accel_y = Column(Float, nullable=True)
    accel_z = Column(Float, nullable=True)

    # Gyroscope
    gyro_x = Column(Float, nullable=True)
    gyro_y = Column(Float, nullable=True)
    gyro_z = Column(Float, nullable=True)

    # Heart rate
    heart_rate = Column(Float, nullable=True)
    ppg = Column(Float, nullable=True)
    ecg = Column(Float, nullable=True)

    # Relationships
    session = relationship("SwimSession", back_populates="sensor_samples")


class SessionResult(Base):
    """ML-computed results for a swim session (1:1 with session)."""
    __tablename__ = "session_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("swim_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)

    lap_count = Column(Integer, nullable=False, default=0)
    total_stroke_count = Column(Integer, nullable=False, default=0)
    avg_lap_time_s = Column(Float, nullable=True)
    avg_velocity_m_s = Column(Float, nullable=True)
    avg_stroke_rate_hz = Column(Float, nullable=True)
    avg_stroke_length_m = Column(Float, nullable=True)
    avg_stroke_index = Column(Float, nullable=True)
    stroke_distribution = Column(JSONB, nullable=True)  # {freestyle: 0.8, ...}
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("SwimSession", back_populates="result")
    laps = relationship("LapResult", back_populates="session_result", cascade="all, delete-orphan")


class LapResult(Base):
    """Per-lap breakdown of a session."""
    __tablename__ = "lap_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_result_id = Column(UUID(as_uuid=True), ForeignKey("session_results.id", ondelete="CASCADE"), nullable=False)

    lap_number = Column(Integer, nullable=False)
    lap_time_s = Column(Float, nullable=False)
    stroke_count = Column(Integer, nullable=False)
    stroke_type = Column(Enum(StrokeType), nullable=True)
    velocity_m_s = Column(Float, nullable=True)
    stroke_rate_hz = Column(Float, nullable=True)
    stroke_length_m = Column(Float, nullable=True)
    stroke_index = Column(Float, nullable=True)

    # Relationships
    session_result = relationship("SessionResult", back_populates="laps")


class Goal(Base):
    """A swimmer's training goal."""
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    swimmer_id = Column(UUID(as_uuid=True), ForeignKey("swimmers.id", ondelete="CASCADE"), nullable=False)
    event_name = Column(String(100), nullable=False)
    target_time_s = Column(Float, nullable=False)
    goal_type = Column(Enum(GoalType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    swimmer = relationship("Swimmer", back_populates="goals")
    progress = relationship("GoalProgress", back_populates="goal", cascade="all, delete-orphan")


class GoalProgress(Base):
    """Progress tracking entry for a goal."""
    __tablename__ = "goal_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("swim_sessions.id", ondelete="SET NULL"), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    projected_time_s = Column(Float, nullable=False)

    # Relationships
    goal = relationship("Goal", back_populates="progress")
