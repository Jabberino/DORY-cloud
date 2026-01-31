"""Initial schema migration.

Revision ID: 001
Revises: 
Create Date: 2026-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums first
    op.execute("CREATE TYPE sex AS ENUM ('M', 'F')")
    op.execute("CREATE TYPE exercisecategory AS ENUM ('sprint', 'distance')")
    op.execute("CREATE TYPE goaltype AS ENUM ('sprint', 'endurance')")
    op.execute("CREATE TYPE stroketype AS ENUM ('freestyle', 'backstroke', 'breaststroke', 'butterfly', 'unknown')")

    # Teams
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('join_code', sa.String(length=8), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('join_code')
    )

    # Coaches
    op.create_table('coaches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Swimmers
    op.create_table('swimmers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('birthday', sa.Date(), nullable=False),
        sa.Column('sex', postgresql.ENUM('M', 'F', name='sex', create_type=False), nullable=False),
        sa.Column('height_cm', sa.Float(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('wingspan_cm', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Team Coaches (junction)
    op.create_table('team_coaches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('coach_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_owner', sa.Boolean(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['coach_id'], ['coaches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'coach_id', name='uq_team_coach')
    )

    # Team Swimmers (junction)
    op.create_table('team_swimmers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('swimmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['swimmer_id'], ['swimmers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'swimmer_id', name='uq_team_swimmer')
    )

    # Exercises
    op.create_table('exercises',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', postgresql.ENUM('sprint', 'distance', name='exercisecategory', create_type=False), nullable=False),
        sa.Column('distance_m', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Swim Sessions
    op.create_table('swim_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('swimmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('pool_length_m', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['swimmer_id'], ['swimmers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Sensor Samples
    op.create_table('sensor_samples',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.BigInteger(), nullable=False),
        sa.Column('accel_x', sa.Float(), nullable=True),
        sa.Column('accel_y', sa.Float(), nullable=True),
        sa.Column('accel_z', sa.Float(), nullable=True),
        sa.Column('gyro_x', sa.Float(), nullable=True),
        sa.Column('gyro_y', sa.Float(), nullable=True),
        sa.Column('gyro_z', sa.Float(), nullable=True),
        sa.Column('heart_rate', sa.Float(), nullable=True),
        sa.Column('ppg', sa.Float(), nullable=True),
        sa.Column('ecg', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['swim_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sensor_samples_session_id', 'sensor_samples', ['session_id'])

    # Session Results
    op.create_table('session_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lap_count', sa.Integer(), nullable=False),
        sa.Column('total_stroke_count', sa.Integer(), nullable=False),
        sa.Column('avg_lap_time_s', sa.Float(), nullable=True),
        sa.Column('avg_velocity_m_s', sa.Float(), nullable=True),
        sa.Column('avg_stroke_rate_hz', sa.Float(), nullable=True),
        sa.Column('avg_stroke_length_m', sa.Float(), nullable=True),
        sa.Column('avg_stroke_index', sa.Float(), nullable=True),
        sa.Column('stroke_distribution', postgresql.JSONB(), nullable=True),
        sa.Column('computed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['swim_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )

    # Lap Results
    op.create_table('lap_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_result_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lap_number', sa.Integer(), nullable=False),
        sa.Column('lap_time_s', sa.Float(), nullable=False),
        sa.Column('stroke_count', sa.Integer(), nullable=False),
        sa.Column('stroke_type', postgresql.ENUM('freestyle', 'backstroke', 'breaststroke', 'butterfly', 'unknown', name='stroketype', create_type=False), nullable=True),
        sa.Column('velocity_m_s', sa.Float(), nullable=True),
        sa.Column('stroke_rate_hz', sa.Float(), nullable=True),
        sa.Column('stroke_length_m', sa.Float(), nullable=True),
        sa.Column('stroke_index', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['session_result_id'], ['session_results.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Goals
    op.create_table('goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('swimmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_name', sa.String(length=100), nullable=False),
        sa.Column('target_time_s', sa.Float(), nullable=False),
        sa.Column('goal_type', postgresql.ENUM('sprint', 'endurance', name='goaltype', create_type=False), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['swimmer_id'], ['swimmers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Goal Progress
    op.create_table('goal_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('projected_time_s', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['swim_sessions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('goal_progress')
    op.drop_table('goals')
    op.drop_table('lap_results')
    op.drop_table('session_results')
    op.drop_index('ix_sensor_samples_session_id', table_name='sensor_samples')
    op.drop_table('sensor_samples')
    op.drop_table('swim_sessions')
    op.drop_table('exercises')
    op.drop_table('team_swimmers')
    op.drop_table('team_coaches')
    op.drop_table('swimmers')
    op.drop_table('coaches')
    op.drop_table('teams')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS stroketype")
    op.execute("DROP TYPE IF EXISTS goaltype")
    op.execute("DROP TYPE IF EXISTS exercisecategory")
    op.execute("DROP TYPE IF EXISTS sex")
