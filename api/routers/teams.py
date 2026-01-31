"""Teams router."""

import secrets
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Team, TeamCoach, TeamSwimmer, Coach, Swimmer
from ..schemas import (
    TeamCreate, TeamResponse, TeamWithMembers,
    CoachBrief, SwimmerBrief, AddCoachToTeam, AddSwimmerToTeam
)

router = APIRouter(prefix="/teams", tags=["teams"])


def generate_join_code() -> str:
    """Generate a random 6-character join code."""
    return secrets.token_urlsafe(4)[:6].upper()


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team."""
    team = Team(
        name=team_data.name,
        join_code=generate_join_code()
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/{team_id}", response_model=TeamWithMembers)
def get_team(team_id: UUID, db: Session = Depends(get_db)):
    """Get team by ID with coaches and swimmers."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Build response with members
    coaches = []
    for tc in team.coaches:
        coaches.append(CoachBrief(
            id=tc.coach.id,
            name=tc.coach.name,
            email=tc.coach.email,
            is_owner=tc.is_owner
        ))
    
    swimmers = []
    for ts in team.swimmers:
        swimmers.append(SwimmerBrief(
            id=ts.swimmer.id,
            name=ts.swimmer.name
        ))
    
    return TeamWithMembers(
        id=team.id,
        name=team.name,
        join_code=team.join_code,
        created_at=team.created_at,
        coaches=coaches,
        swimmers=swimmers
    )


@router.get("/code/{join_code}", response_model=TeamResponse)
def get_team_by_code(join_code: str, db: Session = Depends(get_db)):
    """Get team by join code."""
    team = db.query(Team).filter(Team.join_code == join_code.upper()).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: UUID, db: Session = Depends(get_db)):
    """Delete a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()


# --- Team Coaches ---

@router.get("/{team_id}/coaches", response_model=List[CoachBrief])
def list_team_coaches(team_id: UUID, db: Session = Depends(get_db)):
    """List coaches in a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return [
        CoachBrief(
            id=tc.coach.id,
            name=tc.coach.name,
            email=tc.coach.email,
            is_owner=tc.is_owner
        )
        for tc in team.coaches
    ]


@router.post("/{team_id}/coaches", status_code=status.HTTP_201_CREATED)
def add_coach_to_team(team_id: UUID, data: AddCoachToTeam, db: Session = Depends(get_db)):
    """Add a coach to a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    coach = db.query(Coach).filter(Coach.id == data.coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    # Check if already member
    existing = db.query(TeamCoach).filter(
        TeamCoach.team_id == team_id,
        TeamCoach.coach_id == data.coach_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coach already in team")
    
    tc = TeamCoach(team_id=team_id, coach_id=data.coach_id, is_owner=data.is_owner)
    db.add(tc)
    db.commit()
    return {"message": "Coach added to team"}


@router.delete("/{team_id}/coaches/{coach_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_coach_from_team(team_id: UUID, coach_id: UUID, db: Session = Depends(get_db)):
    """Remove a coach from a team."""
    tc = db.query(TeamCoach).filter(
        TeamCoach.team_id == team_id,
        TeamCoach.coach_id == coach_id
    ).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Coach not in team")
    db.delete(tc)
    db.commit()


# --- Team Swimmers ---

@router.get("/{team_id}/swimmers", response_model=List[SwimmerBrief])
def list_team_swimmers(team_id: UUID, db: Session = Depends(get_db)):
    """List swimmers in a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return [
        SwimmerBrief(id=ts.swimmer.id, name=ts.swimmer.name)
        for ts in team.swimmers
    ]


@router.post("/{team_id}/swimmers", status_code=status.HTTP_201_CREATED)
def add_swimmer_to_team(team_id: UUID, data: AddSwimmerToTeam, db: Session = Depends(get_db)):
    """Add a swimmer to a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    swimmer = db.query(Swimmer).filter(Swimmer.id == data.swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    # Check if already member
    existing = db.query(TeamSwimmer).filter(
        TeamSwimmer.team_id == team_id,
        TeamSwimmer.swimmer_id == data.swimmer_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Swimmer already in team")
    
    ts = TeamSwimmer(team_id=team_id, swimmer_id=data.swimmer_id)
    db.add(ts)
    db.commit()
    return {"message": "Swimmer added to team"}


@router.delete("/{team_id}/swimmers/{swimmer_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_swimmer_from_team(team_id: UUID, swimmer_id: UUID, db: Session = Depends(get_db)):
    """Remove a swimmer from a team."""
    ts = db.query(TeamSwimmer).filter(
        TeamSwimmer.team_id == team_id,
        TeamSwimmer.swimmer_id == swimmer_id
    ).first()
    if not ts:
        raise HTTPException(status_code=404, detail="Swimmer not in team")
    db.delete(ts)
    db.commit()
