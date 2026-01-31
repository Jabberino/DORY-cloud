"""Exercises router."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Exercise, Team, ExerciseCategory
from ..schemas import ExerciseCreate, ExerciseUpdate, ExerciseResponse

router = APIRouter(tags=["exercises"])


@router.post("/teams/{team_id}/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(team_id: UUID, exercise_data: ExerciseCreate, db: Session = Depends(get_db)):
    """Create an exercise template for a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    exercise = Exercise(team_id=team_id, **exercise_data.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.get("/teams/{team_id}/exercises", response_model=List[ExerciseResponse])
def list_team_exercises(
    team_id: UUID,
    category: Optional[ExerciseCategory] = Query(None),
    db: Session = Depends(get_db)
):
    """List exercises for a team, optionally filtered by category."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    query = db.query(Exercise).filter(Exercise.team_id == team_id)
    if category:
        query = query.filter(Exercise.category == category)
    
    return query.all()


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: UUID, db: Session = Depends(get_db)):
    """Get exercise by ID."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(exercise_id: UUID, exercise_data: ExerciseUpdate, db: Session = Depends(get_db)):
    """Update an exercise."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    update_data = exercise_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: UUID, db: Session = Depends(get_db)):
    """Delete an exercise."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    db.delete(exercise)
    db.commit()
