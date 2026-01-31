"""Goals router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Goal, GoalProgress, Swimmer
from ..schemas import (
    GoalCreate, GoalUpdate, GoalResponse, GoalWithProgress,
    GoalProgressCreate, GoalProgressResponse
)

router = APIRouter(tags=["goals"])


@router.post("/swimmers/{swimmer_id}/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(swimmer_id: UUID, goal_data: GoalCreate, db: Session = Depends(get_db)):
    """Create a goal for a swimmer."""
    swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    goal = Goal(swimmer_id=swimmer_id, **goal_data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/swimmers/{swimmer_id}/goals", response_model=List[GoalResponse])
def list_swimmer_goals(swimmer_id: UUID, db: Session = Depends(get_db)):
    """List all goals for a swimmer."""
    swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    return db.query(Goal).filter(Goal.swimmer_id == swimmer_id).all()


@router.get("/goals/{goal_id}", response_model=GoalWithProgress)
def get_goal(goal_id: UUID, db: Session = Depends(get_db)):
    """Get goal with progress history."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: UUID, goal_data: GoalUpdate, db: Session = Depends(get_db)):
    """Update a goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    update_data = goal_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: UUID, db: Session = Depends(get_db)):
    """Delete a goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()


@router.post("/goals/{goal_id}/progress", response_model=GoalProgressResponse, status_code=status.HTTP_201_CREATED)
def add_progress(goal_id: UUID, progress_data: GoalProgressCreate, db: Session = Depends(get_db)):
    """Add a progress entry to a goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    progress = GoalProgress(goal_id=goal_id, **progress_data.model_dump())
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress
