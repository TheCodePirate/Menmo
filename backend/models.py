"""SQLAlchemy models representing backend persistence layer."""
from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampedModel:
    """Mixin providing created/updated timestamps."""

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserProfile(TimestampedModel, Base):
    """Represents a user profile stored in the database."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    organization = Column(String(255), nullable=True)
    focus_areas = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    entity_type = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    company_size = Column(String(100), nullable=True)
    project_type = Column(String(255), nullable=True)
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)

    matches = relationship("Match", back_populates="user", cascade="all, delete-orphan")
    projects = relationship(
        "ProjectProfile", back_populates="user", cascade="all, delete-orphan"
    )
    quick_scans = relationship(
        "QuickScanResult", back_populates="user", cascade="all, delete-orphan"
    )
    evidence = relationship(
        "EvidenceRequirementStatus",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    deadlines = relationship(
        "DeadlineMilestone",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Grant(TimestampedModel, Base):
    """Represents an available grant."""

    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    sponsor = Column(String(255), nullable=True)
    deadline = Column(String(100), nullable=True)
    url = Column(String(512), nullable=True)
    jurisdiction = Column(String(255), nullable=True)
    entity_types = Column(JSON, nullable=False, default=list)
    industries = Column(JSON, nullable=False, default=list)
    project_types = Column(JSON, nullable=False, default=list)
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    min_co2_reduction = Column(Float, nullable=True)
    max_support = Column(Float, nullable=True)
    support_unit = Column(String(50), nullable=True)
    rules = Column(JSON, nullable=False, default=list)
    proprietary_notes = Column(JSON, nullable=False, default=list)
    deadlines = Column(JSON, nullable=False, default=list)

    matches = relationship("Match", back_populates="grant", cascade="all, delete-orphan")
    evidence = relationship(
        "EvidenceRequirementStatus",
        back_populates="grant",
        cascade="all, delete-orphan",
    )
    application_sections = relationship(
        "ApplicationSection",
        back_populates="grant",
        cascade="all, delete-orphan",
    )
    deadlines_config = relationship(
        "DeadlineMilestone",
        back_populates="grant",
        cascade="all, delete-orphan",
    )


class Match(TimestampedModel, Base):
    """Represents a stored match score between a user and a grant."""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    grant_id = Column(
        Integer, ForeignKey("grants.id", ondelete="CASCADE"), nullable=False
    )
    score = Column(Float, nullable=False)
    reasons = Column(JSON, nullable=False, default=list)
    blockers = Column(JSON, nullable=False, default=list)
    citations = Column(JSON, nullable=False, default=list)
    status = Column(String(50), nullable=False, default="pending")
    insights = Column(JSON, nullable=False, default=dict)

    user = relationship("UserProfile", back_populates="matches")
    grant = relationship("Grant", back_populates="matches")
    tasks = relationship(
        "RemediationTask", back_populates="match", cascade="all, delete-orphan"
    )
    application_sections = relationship(
        "ApplicationSection",
        back_populates="match",
        cascade="all, delete-orphan",
    )


class ProjectProfile(TimestampedModel, Base):
    """Captures the richer project description used during deep matching."""

    __tablename__ = "project_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    description = Column(Text, nullable=False)
    capex = Column(Float, nullable=True)
    opex = Column(Float, nullable=True)
    timeline = Column(String(255), nullable=True)
    co2e_reduction = Column(Float, nullable=True)
    partners = Column(Text, nullable=True)

    user = relationship("UserProfile", back_populates="projects")


class QuickScanResult(TimestampedModel, Base):
    """Stores the outcome of the eligibility quick scan for traceability."""

    __tablename__ = "quick_scan_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    grant_id = Column(
        Integer, ForeignKey("grants.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String(20), nullable=False)
    reasons = Column(JSON, nullable=False, default=list)
    blockers = Column(JSON, nullable=False, default=list)
    citations = Column(JSON, nullable=False, default=list)

    user = relationship("UserProfile", back_populates="quick_scans")
    grant = relationship("Grant")


class RemediationTask(TimestampedModel, Base):
    """Represents a blocker converted into an actionable task."""

    __tablename__ = "remediation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(
        Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="todo")
    owner = Column(String(255), nullable=True)
    due_date = Column(Date, nullable=True)
    citation = Column(JSON, nullable=False, default=dict)
    rule_id = Column(String(100), nullable=True)

    match = relationship("Match", back_populates="tasks")


class ApplicationSection(TimestampedModel, Base):
    """Draft content for each section of the application builder."""

    __tablename__ = "application_sections"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(
        Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    grant_id = Column(
        Integer, ForeignKey("grants.id", ondelete="CASCADE"), nullable=False
    )
    key = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    draft = Column(Text, nullable=False)
    assumptions = Column(JSON, nullable=False, default=list)
    citations = Column(JSON, nullable=False, default=list)
    compliance = Column(JSON, nullable=False, default=dict)
    status = Column(String(50), nullable=False, default="suggested")

    match = relationship("Match", back_populates="application_sections")
    grant = relationship("Grant", back_populates="application_sections")


class EvidenceRequirementStatus(TimestampedModel, Base):
    """Tracks evidence items supplied against requirements."""

    __tablename__ = "evidence_requirements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    grant_id = Column(
        Integer, ForeignKey("grants.id", ondelete="CASCADE"), nullable=False
    )
    requirement = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="missing")
    notes = Column(Text, nullable=True)
    citation = Column(JSON, nullable=False, default=dict)

    user = relationship("UserProfile", back_populates="evidence")
    grant = relationship("Grant", back_populates="evidence")


class DeadlineMilestone(TimestampedModel, Base):
    """Stores grant deadlines and user-defined milestones for reminders."""

    __tablename__ = "deadline_milestones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    grant_id = Column(
        Integer, ForeignKey("grants.id", ondelete="CASCADE"), nullable=False
    )
    label = Column(String(255), nullable=False)
    due_date = Column(Date, nullable=False)
    is_grant_deadline = Column(Boolean, nullable=False, default=False)
    source = Column(String(255), nullable=True)

    user = relationship("UserProfile", back_populates="deadlines")
    grant = relationship("Grant", back_populates="deadlines_config")
