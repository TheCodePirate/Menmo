"""FastAPI entrypoint for the Menmo backend service."""

from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend import matching
from backend.db import get_db, init_db
from backend.models import Grant, User

app = FastAPI(title="Menmo Backend", version="0.1.0")


class UserBase(BaseModel):
    name: str
    email: str
    organization: str | None = None
    interests: str
    goals: str | None = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True


class GrantBase(BaseModel):
    title: str
    description: str
    focus_area: str | None = None
    sponsor: str | None = None


class GrantCreate(GrantBase):
    pass


class GrantRead(GrantBase):
    id: int

    class Config:
        orm_mode = True


class GrantMatch(BaseModel):
    grant: GrantRead
    score: float


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/users/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with that email already exists.")

    db_user = User(
        name=user.name,
        email=user.email,
        organization=user.organization,
        interests=user.interests,
        goals=user.goals,
    )
    db.add(db_user)
    db.flush()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/grants/", response_model=GrantRead, status_code=201)
def create_grant(grant: GrantCreate, db: Session = Depends(get_db)) -> Grant:
    db_grant = Grant(
        title=grant.title,
        description=grant.description,
        focus_area=grant.focus_area,
        sponsor=grant.sponsor,
    )
    db.add(db_grant)
    db.flush()
    db.refresh(db_grant)
    return db_grant


@app.get("/grants/", response_model=List[GrantRead])
def list_grants(db: Session = Depends(get_db)) -> List[Grant]:
    return db.query(Grant).all()


@app.post("/matches/{user_id}", response_model=List[GrantMatch])
def generate_matches(
    user_id: int,
    top_k: int = 5,
    db: Session = Depends(get_db),
) -> List[GrantMatch]:
    try:
        results = matching.rank_grants_for_user(db, user_id=user_id, top_k=top_k)
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [GrantMatch(grant=GrantRead.from_orm(result.grant), score=result.score) for result in results]
