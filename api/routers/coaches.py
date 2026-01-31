"""Coaches router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Coach, TeamCoach
from ..schemas import CoachCreate, CoachResponse, TeamResponse

router = APIRouter(prefix="/coaches", tags=["coaches"])


@router.post("", response_model=CoachResponse, status_code=status.HTTP_201_CREATED)
def create_coach(coach_data: CoachCreate, db: Session = Depends(get_db)):
    """Create a new coach."""
    # Check email uniqueness
    existing = db.query(Coach).filter(Coach.email == coach_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    coach = Coach(name=coach_data.name, email=coach_data.email)
    db.add(coach)
    db.commit()
    db.refresh(coach)
    return coach


@router.get("/{coach_id}", response_model=CoachResponse)
def get_coach(coach_id: UUID, db: Session = Depends(get_db)):
    """Get coach by ID."""
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach


@router.get("/{coach_id}/teams", response_model=List[TeamResponse])
def list_coach_teams(coach_id: UUID, db: Session = Depends(get_db)):
    """List teams for a coach."""
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    return [tc.team for tc in coach.teams]
