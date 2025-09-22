"""Database models for the Menmo backend service."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text

from backend.db import Base


class User(Base):
    """A user profile that can receive grant recommendations."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    organization = Column(String(255), nullable=True)
    interests = Column(Text, nullable=False)
    goals = Column(Text, nullable=True)


class Grant(Base):
    """A funding opportunity available to users."""

    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    focus_area = Column(String(255), nullable=True)
    sponsor = Column(String(255), nullable=True)
