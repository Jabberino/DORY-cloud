"""Swimmers router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Swimmer
from ..schemas import SwimmerCreate, SwimmerUpdate, SwimmerResponse

router = APIRouter(prefix="/swimmers", tags=["swimmers"])


@router.post("", response_model=SwimmerResponse, status_code=status.HTTP_201_CREATED)
def create_swimmer(swimmer_data: SwimmerCreate, db: Session = Depends(get_db)):
    """Create a new swimmer profile."""
    # Check email uniqueness if provided
    if swimmer_data.email:
        existing = db.query(Swimmer).filter(Swimmer.email == swimmer_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    swimmer = Swimmer(**swimmer_data.model_dump())
    db.add(swimmer)
    db.commit()
    db.refresh(swimmer)
    return swimmer


@router.get("/{swimmer_id}", response_model=SwimmerResponse)
def get_swimmer(swimmer_id: UUID, db: Session = Depends(get_db)):
    """Get swimmer by ID."""
    swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    return swimmer


@router.put("/{swimmer_id}", response_model=SwimmerResponse)
def update_swimmer(swimmer_id: UUID, swimmer_data: SwimmerUpdate, db: Session = Depends(get_db)):
    """Update swimmer profile."""
    swimmer = db.query(Swimmer).filter(Swimmer.id == swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    # Update only provided fields
    update_data = swimmer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(swimmer, field, value)
    
    db.commit()
    db.refresh(swimmer)
    return swimmer
