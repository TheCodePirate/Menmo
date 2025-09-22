"""FastAPI application exposing Menmo's multi-stage customer journey."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Mapping, Optional, Sequence

from fastapi import Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from .db import engine, get_session
from .journey import JourneyService
from .models import (
    Base,
    DeadlineMilestone,
    Grant,
    Match,
    RemediationTask,
    UserProfile,
)

app = FastAPI(title="Menmo Journey API", version="0.2.0")


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class Citation(BaseModel):
    title: str
    section: Optional[str] = None
    url: Optional[str] = None
    source_type: Optional[str] = Field(default=None, description="public|proprietary")


class RulePayload(BaseModel):
    id: str
    text: str
    field: Optional[str] = None
    operator: Optional[str] = "equals"
    value: Any = None
    severity: Optional[str] = "required"
    category: Optional[str] = "eligibility"
    citation: Citation | Dict[str, Any]


class ProprietaryNotePayload(BaseModel):
    id: str
    category: str
    text: str
    citation: Citation | Dict[str, Any]


class DeadlinePayload(BaseModel):
    label: str
    due: str
    source: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    email: str
    organization: Optional[str] = None
    focus_areas: Optional[str] = None
    goals: Optional[str] = None
    industry: Optional[str] = None
    entity_type: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    project_type: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None


class UserRead(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GrantCreate(BaseModel):
    title: str
    description: str
    sponsor: Optional[str] = None
    deadline: Optional[str] = None
    url: Optional[str] = None
    jurisdiction: Optional[str] = None
    entity_types: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    project_types: List[str] = Field(default_factory=list)
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    min_co2_reduction: Optional[float] = None
    max_support: Optional[float] = None
    support_unit: Optional[str] = None
    rules: List[RulePayload] = Field(default_factory=list)
    proprietary_notes: List[ProprietaryNotePayload] = Field(default_factory=list)
    deadlines: List[DeadlinePayload] = Field(default_factory=list)


class GrantRead(GrantCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class QuickScanRequest(BaseModel):
    user_id: int
    industry: Optional[str] = None
    entity_type: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    project_type: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None


class QuickScanItem(BaseModel):
    grant_id: int
    grant_title: str
    status: str
    reasons: List[Dict[str, Any]]
    blockers: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]


class FundingMatchRequest(BaseModel):
    user_id: int
    project_description: str
    capex: Optional[float] = None
    opex: Optional[float] = None
    timeline: Optional[str] = None
    co2_reduction: Optional[float] = None
    partners: Optional[str] = None
    top_k: int = 5


class MatchResponse(BaseModel):
    id: int
    grant: GrantRead
    score: float
    status: str
    reasons: List[Dict[str, Any]]
    blockers: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    insights: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class GapPlanRequest(BaseModel):
    match_id: int
    assignments: Dict[str, str] = Field(default_factory=dict)
    default_owner: Optional[str] = None
    default_due_in_days: int = 14


class TaskRead(BaseModel):
    id: int
    title: str
    status: str
    owner: Optional[str]
    due_date: Optional[str]
    citation: Dict[str, Any]
    rule_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    owner: Optional[str] = None


class ApplicationDraftRequest(BaseModel):
    match_id: int
    sections: Optional[List[str]] = None


class ApplicationSectionRead(BaseModel):
    id: int
    key: str
    title: str
    draft: str
    assumptions: List[str]
    citations: List[Dict[str, Any]]
    compliance: Dict[str, Any]
    status: str

    model_config = ConfigDict(from_attributes=True)


class EvidenceDocument(BaseModel):
    requirement: str
    file_name: Optional[str] = None
    notes: Optional[str] = None


class EvidenceCheckRequest(BaseModel):
    match_id: int
    documents: List[EvidenceDocument] = Field(default_factory=list)


class EvidenceRead(BaseModel):
    id: int
    requirement: str
    status: str
    notes: Optional[str]
    citation: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class DeadlineSyncRequest(BaseModel):
    match_id: int
    milestones: Optional[List[Dict[str, Any]]] = None


class DeadlineRead(BaseModel):
    id: int
    label: str
    due_date: date
    is_grant_deadline: bool
    source: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class FinalisationRequest(BaseModel):
    match_id: int


class FinalisationResponse(BaseModel):
    match_id: int
    ready_for_export: bool
    tasks: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]


class PostSubmissionRequest(BaseModel):
    match_id: int


class PostSubmissionResponse(BaseModel):
    match_id: int
    grant: str
    updates: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Lifecycle Hooks
# ---------------------------------------------------------------------------
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# User & Grant management
# ---------------------------------------------------------------------------
@app.post("/users", response_model=UserRead, status_code=201)
def create_user(user_in: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    existing = session.query(UserProfile).filter(UserProfile.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = UserProfile(**user_in.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)) -> UserRead:
    user = session.query(UserProfile).filter(UserProfile.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/grants", response_model=List[GrantRead], status_code=201)
def ingest_grants(
    grants: Sequence[GrantCreate], session: Session = Depends(get_session)
) -> List[GrantRead]:
    grant_models = []
    for grant_payload in grants:
        grant = Grant(**grant_payload.model_dump())
        grant_models.append(grant)
        session.add(grant)
    session.commit()
    for grant in grant_models:
        session.refresh(grant)
    return grant_models


@app.get("/grants", response_model=List[GrantRead])
def list_grants(session: Session = Depends(get_session)) -> List[GrantRead]:
    return session.query(Grant).order_by(Grant.created_at.desc()).all()


# ---------------------------------------------------------------------------
# Stage 1 – Quick Scan
# ---------------------------------------------------------------------------
@app.post("/journey/quick-scan", response_model=List[QuickScanItem])
def quick_scan(
    payload: QuickScanRequest, session: Session = Depends(get_session)
) -> List[QuickScanItem]:
    user = _get_user(session, payload.user_id)
    service = JourneyService(session)
    results = service.run_quick_scan(user=user, payload=payload.model_dump())
    response: List[QuickScanItem] = []
    for result in results:
        response.append(
            QuickScanItem(
                grant_id=result.grant_id,
                grant_title=result.grant.title,
                status=result.status,
                reasons=result.reasons,
                blockers=result.blockers,
                citations=result.citations,
            )
        )
    return response


# ---------------------------------------------------------------------------
# Stage 2 – Funding Match
# ---------------------------------------------------------------------------
@app.post("/journey/funding-match", response_model=List[MatchResponse])
def funding_match(
    payload: FundingMatchRequest, session: Session = Depends(get_session)
) -> List[MatchResponse]:
    user = _get_user(session, payload.user_id)
    service = JourneyService(session)
    matches = service.run_funding_match(
        user=user,
        project_payload=payload.model_dump(),
        top_k=payload.top_k,
    )
    response: List[MatchResponse] = []
    for match in matches:
        response.append(
            MatchResponse(
                id=match.id,
                grant=match.grant,
                score=match.score,
                status=match.status,
                reasons=match.reasons,
                blockers=match.blockers,
                citations=match.citations,
                insights=match.insights,
            )
        )
    return response


# ---------------------------------------------------------------------------
# Stage 3 – Gap-to-Yes planner
# ---------------------------------------------------------------------------
@app.post("/journey/gap-plan", response_model=List[TaskRead])
def gap_plan(
    payload: GapPlanRequest, session: Session = Depends(get_session)
) -> List[TaskRead]:
    match = _get_match(session, payload.match_id)
    service = JourneyService(session)
    tasks = service.build_gap_plan(
        match=match,
        assignments=payload.assignments,
        default_owner=payload.default_owner,
        default_due_in_days=payload.default_due_in_days,
    )
    return [
        TaskRead(
            id=task.id,
            title=task.title,
            status=task.status,
            owner=task.owner,
            due_date=task.due_date.isoformat() if task.due_date else None,
            citation=task.citation,
            rule_id=task.rule_id,
        )
        for task in tasks
    ]


@app.patch("/journey/tasks/{task_id}", response_model=TaskRead)
def update_task(
    payload: TaskUpdate,
    task_id: int = Path(..., description="Task identifier"),
    session: Session = Depends(get_session),
) -> TaskRead:
    task = session.query(RemediationTask).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.status is not None:
        task.status = payload.status
    if payload.owner is not None:
        task.owner = payload.owner
    session.commit()
    session.refresh(task)
    return TaskRead(
        id=task.id,
        title=task.title,
        status=task.status,
        owner=task.owner,
        due_date=task.due_date.isoformat() if task.due_date else None,
        citation=task.citation,
        rule_id=task.rule_id,
    )


# ---------------------------------------------------------------------------
# Stage 4 – Application Builder
# ---------------------------------------------------------------------------
@app.post("/journey/application-draft", response_model=List[ApplicationSectionRead])
def application_draft(
    payload: ApplicationDraftRequest, session: Session = Depends(get_session)
) -> List[ApplicationSectionRead]:
    match = _get_match(session, payload.match_id)
    service = JourneyService(session)
    sections = service.generate_application_sections(
        match=match,
        requested_sections=payload.sections,
    )
    return [
        ApplicationSectionRead(
            id=section.id,
            key=section.key,
            title=section.title,
            draft=section.draft,
            assumptions=section.assumptions,
            citations=section.citations,
            compliance=section.compliance,
            status=section.status,
        )
        for section in sections
    ]


# ---------------------------------------------------------------------------
# Stage 5 – Evidence AutoCheck
# ---------------------------------------------------------------------------
@app.post("/journey/evidence-check", response_model=List[EvidenceRead])
def evidence_check(
    payload: EvidenceCheckRequest, session: Session = Depends(get_session)
) -> List[EvidenceRead]:
    match = _get_match(session, payload.match_id)
    service = JourneyService(session)
    records = service.evaluate_evidence(match=match, documents=[doc.model_dump() for doc in payload.documents])
    return [
        EvidenceRead(
            id=record.id,
            requirement=record.requirement,
            status=record.status,
            notes=record.notes,
            citation=record.citation,
        )
        for record in records
    ]


# ---------------------------------------------------------------------------
# Stage 6 – Deadline Radar
# ---------------------------------------------------------------------------
@app.post("/journey/deadlines", response_model=List[DeadlineRead])
def sync_deadlines(
    payload: DeadlineSyncRequest, session: Session = Depends(get_session)
) -> List[DeadlineRead]:
    match = _get_match(session, payload.match_id)
    service = JourneyService(session)
    deadlines = service.sync_deadlines(match=match, milestones=payload.milestones)
    return [
        DeadlineRead(
            id=item.id,
            label=item.label,
            due_date=item.due_date,
            is_grant_deadline=item.is_grant_deadline,
            source=item.source,
        )
        for item in deadlines
    ]


@app.get("/journey/deadlines/{user_id}", response_model=List[DeadlineRead])
def list_deadlines(user_id: int, session: Session = Depends(get_session)) -> List[DeadlineRead]:
    _get_user(session, user_id)
    deadlines = (
        session.query(DeadlineMilestone)
        .filter(DeadlineMilestone.user_id == user_id)
        .order_by(DeadlineMilestone.due_date)
        .all()
    )
    return deadlines


# ---------------------------------------------------------------------------
# Stage 7 – Finalisation snapshot
# ---------------------------------------------------------------------------
@app.post("/journey/finalise", response_model=FinalisationResponse)
def finalise(
    payload: FinalisationRequest, session: Session = Depends(get_session)
) -> FinalisationResponse:
    match = _get_match(session, payload.match_id)
    service = JourneyService(session)
    snapshot = service.generate_finalisation_snapshot(match)
    return FinalisationResponse(**snapshot)


# ---------------------------------------------------------------------------
# Stage 8 – Post submission updates
# ---------------------------------------------------------------------------
@app.post("/journey/post-submission", response_model=PostSubmissionResponse)
def post_submission(
    payload: PostSubmissionRequest, session: Session = Depends(get_session)
) -> PostSubmissionResponse:
    match = _get_match(session, payload.match_id)
    service = JourneyService(session)
    data = service.post_submission_updates(match)
    return PostSubmissionResponse(**data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_user(session: Session, user_id: int) -> UserProfile:
    user = session.query(UserProfile).filter(UserProfile.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _get_match(session: Session, match_id: int) -> Match:
    match = session.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
