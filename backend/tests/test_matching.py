from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.matching import MatchingService
from backend.models import Base, Grant, UserProfile


@pytest.fixture()
def session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_matching_ranks_high_relevance_grant(session: Session) -> None:
    user = UserProfile(
        name="Researcher One",
        email="researcher@example.com",
        focus_areas="artificial intelligence, machine learning",
        goals="advance trustworthy ai",
    )
    session.add(user)

    grants = [
        Grant(
            title="AI Safety Research Grant",
            description="Funding for research into responsible and trustworthy artificial intelligence.",
            sponsor="Tech Philanthropy",
        ),
        Grant(
            title="Marine Biology Fellowship",
            description="Support for oceanic wildlife preservation studies.",
            sponsor="Oceanic Trust",
        ),
    ]
    session.add_all(grants)
    session.commit()

    service = MatchingService(model_name="test")
    matches = service.generate_matches(session=session, user=user, top_k=2)

    assert len(matches) == 2
    assert matches[0].grant.title == "AI Safety Research Grant"
    assert matches[0].score >= matches[1].score


def test_matching_handles_no_grants(session: Session) -> None:
    user = UserProfile(name="Solo User", email="solo@example.com")
    session.add(user)
    session.commit()

    service = MatchingService(model_name="test")
    matches = service.generate_matches(session=session, user=user, top_k=5)

    assert matches == []
