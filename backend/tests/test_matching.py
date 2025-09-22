"""Tests for the Menmo matching engine."""

from __future__ import annotations

import pathlib
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure the backend package is importable when running the tests directly.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import Base
from backend.matching import rank_grants_for_user
from backend.models import Grant, User


def setup_test_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_rank_grants_prioritizes_relevant_content() -> None:
    session = setup_test_session()

    try:
        user = User(
            name="Alice",
            email="alice@example.com",
            organization="Green Earth",
            interests="climate change sustainability renewable energy",
            goals="Expand solar installations across communities",
        )
        session.add(user)

        grants = [
            Grant(
                title="Community Solar Expansion",
                description="Funding for renewable energy and solar panel deployment",
                focus_area="Climate",
                sponsor="Sunshine Foundation",
            ),
            Grant(
                title="Arts Education Grant",
                description="Support for arts programs in schools",
                focus_area="Education",
                sponsor="Creative Minds",
            ),
        ]
        session.add_all(grants)
        session.commit()

        matches = rank_grants_for_user(session, user.id, top_k=2)

        assert matches[0].grant.title == "Community Solar Expansion"
        assert matches[0].score > matches[1].score
    finally:
        session.close()


def test_rank_grants_handles_missing_user() -> None:
    session = setup_test_session()
    try:
        try:
            rank_grants_for_user(session, user_id=999)
        except ValueError as exc:
            assert "was not found" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected ValueError for missing user")
    finally:
        session.close()
