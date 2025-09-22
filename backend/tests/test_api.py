from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))


from typing import Generator, List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db import get_session
from backend.main import app
from backend.models import Base


@pytest.fixture()
def session() -> Generator[Session, None, None]:
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


@pytest.fixture()
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        try:
            yield session
        finally:
            session.rollback()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _ingest_sample_grants(client: TestClient) -> List[int]:
    payload = [
        {
            "title": "Klimatklivet",
            "description": "Support for Swedish climate mitigation investments such as EV charging.",
            "deadline": "2024-11-30",
            "url": "https://www.naturvardsverket.se/klimatklivet",
            "jurisdiction": "Sweden",
            "entity_types": ["SME", "Municipality"],
            "industries": ["transport", "energy"],
            "project_types": ["ev charging", "energy efficiency"],
            "budget_min": 50000,
            "budget_max": 5000000,
            "min_co2_reduction": 50,
            "max_support": 700000,
            "support_unit": "SEK",
            "rules": [
                {
                    "id": "KLIM-ELIG-ENTITY",
                    "text": "Applicants must be SMEs or municipalities registered in Sweden.",
                    "field": "entity_type",
                    "operator": "in",
                    "value": ["sme", "municipality"],
                    "severity": "required",
                    "category": "eligibility",
                    "citation": {
                        "title": "Klimatklivet Handbook 2023",
                        "section": "2.1",
                    },
                },
                {
                    "id": "KLIM-ELIG-LOC",
                    "text": "Projects must be executed in Sweden.",
                    "field": "location",
                    "operator": "equals",
                    "value": "Sweden",
                    "severity": "required",
                    "category": "eligibility",
                    "citation": {
                        "title": "Klimatklivet Handbook 2023",
                        "section": "1.1",
                    },
                },
                {
                    "id": "KLIM-BUDGET",
                    "text": "Eligible budget between 50k and 5M SEK.",
                    "field": "budget_min",
                    "operator": "range",
                    "value": {"min": 50000, "max": 5000000},
                    "severity": "preferred",
                    "category": "fit",
                    "citation": {
                        "title": "Klimatklivet Budget Guidance",
                        "section": "4.2",
                    },
                },
                {
                    "id": "KLIM-PROJECT",
                    "text": "EV fast chargers of at least 150 kW are prioritised.",
                    "field": "project_description",
                    "operator": "contains",
                    "value": ["charger", "fast"],
                    "severity": "preferred",
                    "category": "fit",
                    "citation": {
                        "title": "Stockholm EV Infrastructure Memo",
                        "section": "3.4",
                        "source_type": "proprietary",
                    },
                },
            ],
            "proprietary_notes": [
                {
                    "id": "KLIM-EVID-BASELINE",
                    "category": "evidence",
                    "text": "Submit baseline CO2 inventory using Stockholm municipality template.",
                    "citation": {
                        "title": "Stockholm EV Infrastructure Memo",
                        "section": "3.4",
                        "source_type": "proprietary",
                    },
                },
                {
                    "id": "KLIM-UPDATE-2024",
                    "category": "update",
                    "text": "Municipal co-funding requirement expected to increase in 2025.",
                    "citation": {
                        "title": "Municipal Partner Brief",
                        "section": "1.0",
                        "source_type": "proprietary",
                    },
                },
            ],
            "deadlines": [
                {"label": "Application deadline", "due": "2024-11-30"}
            ],
        },
        {
            "title": "Horizon Europe Mission",
            "description": "European mission for climate neutral cities with cross-border collaboration.",
            "deadline": "2025-02-15",
            "url": "https://research-and-innovation.ec.europa.eu",
            "jurisdiction": "EU",
            "entity_types": ["SME", "Consortium"],
            "industries": ["energy", "mobility"],
            "project_types": ["urban innovation"],
            "min_co2_reduction": 100,
            "max_support": 2000000,
            "support_unit": "EUR",
            "rules": [
                {
                    "id": "EU-PARTNERS",
                    "text": "Requires international partnerships with at least two EU member states.",
                    "field": "partners",
                    "operator": "contains",
                    "value": ["international"],
                    "severity": "required",
                    "category": "eligibility",
                    "citation": {
                        "title": "Horizon Europe Work Programme",
                        "section": "1.2.5",
                    },
                }
            ],
            "proprietary_notes": [],
            "deadlines": [
                {"label": "Concept note", "due": "2024-09-01"},
                {"label": "Full proposal", "due": "2025-02-15"},
            ],
        },
    ]

    response = client.post("/grants", json=payload)
    assert response.status_code == 201, response.text
    return [grant["id"] for grant in response.json()]


def test_end_to_end_journey(client: TestClient) -> None:
    user_payload = {
        "name": "Stockholm Mobility",
        "email": "mobility@example.com",
        "organization": "Stockholm Mobility Lab",
        "entity_type": "SME",
        "location": "Sweden",
        "industry": "transport",
        "project_type": "ev charging",
        "budget_min": 150000,
        "budget_max": 450000,
    }
    user_response = client.post("/users", json=user_payload)
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    _ingest_sample_grants(client)

    quick_scan_payload = {
        "user_id": user_id,
        "industry": "transport",
        "entity_type": "SME",
        "location": "Sweden",
        "project_type": "ev charging",
        "budget_min": 200000,
        "budget_max": 500000,
    }
    quick_response = client.post("/journey/quick-scan", json=quick_scan_payload)
    assert quick_response.status_code == 200
    quick_items = quick_response.json()
    assert len(quick_items) == 2
    klimat_status = next(item for item in quick_items if item["grant_title"] == "Klimatklivet")
    assert klimat_status["status"] in {"Yes", "Maybe"}

    match_payload = {
        "user_id": user_id,
        "project_description": "Deploy 6 smart EV chargers rated 120kW across Stockholm's logistics hubs.",
        "capex": 350000,
        "opex": 25000,
        "timeline": "2024-2025",
        "co2_reduction": 180.5,
        "partners": "Local utility, municipal transport agency",
        "top_k": 2,
    }
    match_response = client.post("/journey/funding-match", json=match_payload)
    assert match_response.status_code == 200
    matches = match_response.json()
    assert len(matches) == 2
    top_match = matches[0]
    assert top_match["grant"]["title"] == "Klimatklivet"
    assert any(reason["id"] == "KLIM-ELIG-ENTITY" for reason in top_match["reasons"])

    gap_payload = {
        "match_id": top_match["id"],
        "assignments": {"KLIM-PROJECT": "Mobility Lead"},
        "default_owner": "Grants Team",
        "default_due_in_days": 10,
    }
    gap_response = client.post("/journey/gap-plan", json=gap_payload)
    assert gap_response.status_code == 200
    tasks = gap_response.json()
    assert tasks
    first_task_id = tasks[0]["id"]

    update_response = client.patch(
        f"/journey/tasks/{first_task_id}", json={"status": "in_progress"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"

    draft_response = client.post(
        "/journey/application-draft",
        json={"match_id": top_match["id"], "sections": ["summary", "budget"]},
    )
    assert draft_response.status_code == 200
    drafts = draft_response.json()
    assert len(drafts) == 2
    assert drafts[0]["key"] == "summary"
    assert drafts[0]["citations"]

    evidence_response = client.post(
        "/journey/evidence-check",
        json={
            "match_id": top_match["id"],
            "documents": [
                {"requirement": "KLIM-EVID-BASELINE", "file_name": "baseline.pdf"}
            ],
        },
    )
    assert evidence_response.status_code == 200
    evidence_items = evidence_response.json()
    assert evidence_items[0]["status"] in {"missing", "compliant"}

    deadlines_response = client.post(
        "/journey/deadlines",
        json={
            "match_id": top_match["id"],
            "milestones": [{"label": "Internal review", "due": "2024-10-01"}],
        },
    )
    assert deadlines_response.status_code == 200
    assert any(item["is_grant_deadline"] for item in deadlines_response.json())

    finalise_response = client.post(
        "/journey/finalise", json={"match_id": top_match["id"]}
    )
    assert finalise_response.status_code == 200
    finalise_data = finalise_response.json()
    assert finalise_data["match_id"] == top_match["id"]

    post_response = client.post(
        "/journey/post-submission", json={"match_id": top_match["id"]}
    )
    assert post_response.status_code == 200
    assert post_response.json()["updates"]
