"""Business logic orchestrating the Menmo customer journey stages."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from sqlalchemy.orm import Session

from .matching import MatchingService, SimpleTfidfEncoder, _cosine_similarity
from .models import (
    ApplicationSection,
    DeadlineMilestone,
    EvidenceRequirementStatus,
    Grant,
    Match,
    ProjectProfile,
    QuickScanResult,
    RemediationTask,
    UserProfile,
)
from .rag import RAGEngine


APPLICATION_SECTIONS: List[Dict[str, str]] = [
    {"key": "summary", "title": "Project Summary"},
    {"key": "objectives", "title": "Objectives"},
    {"key": "climate_impact", "title": "Climate Impact"},
    {"key": "budget", "title": "Budget"},
    {"key": "risk", "title": "Risk & Mitigation"},
]


@dataclass
class RuleEvaluation:
    """Represents the evaluation outcome of a single rule."""

    id: str
    text: str
    citation: Mapping[str, Any]
    passed: bool
    severity: str
    category: str


def _normalize(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _coerce_to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _tokenize_keywords(value: Optional[str]) -> List[str]:
    encoder = SimpleTfidfEncoder()
    if not value:
        return []
    return encoder._tokenize(value)


class JourneyService:
    """High-level service implementing the Menmo journey stages."""

    def __init__(self, session: Session):
        self.session = session
        self.matching_service = MatchingService()
        self.rag_engine = RAGEngine()

    # ------------------------------------------------------------------
    # Stage 1 – Quick Scan
    # ------------------------------------------------------------------
    def run_quick_scan(
        self,
        user: UserProfile,
        payload: Mapping[str, Any],
    ) -> List[QuickScanResult]:
        """Evaluate quick eligibility for all grants and persist results."""

        for field in [
            "industry",
            "entity_type",
            "location",
            "company_size",
            "project_type",
            "budget_min",
            "budget_max",
        ]:
            if field in payload:
                setattr(user, field, payload[field])

        self.session.query(QuickScanResult).filter_by(user_id=user.id).delete(
            synchronize_session=False
        )

        grants = self.session.query(Grant).all()
        results: List[QuickScanResult] = []
        payload = dict(payload)
        for grant in grants:
            evaluation = self._evaluate_grant_rules(grant, payload)
            status = self._derive_status(evaluation)
            reasons = [
                {
                    "id": item.id,
                    "text": item.text,
                    "citation": item.citation,
                }
                for item in evaluation
                if item.passed and item.category in {"eligibility", "fit"}
            ]
            blockers = [
                {
                    "id": item.id,
                    "text": item.text,
                    "citation": item.citation,
                }
                for item in evaluation
                if not item.passed
            ]
            citations = [item.citation for item in evaluation]

            result = QuickScanResult(
                user=user,
                grant=grant,
                status=status,
                reasons=reasons,
                blockers=blockers,
                citations=citations,
            )
            self.session.add(result)
            results.append(result)

        self.session.commit()
        return results

    # ------------------------------------------------------------------
    # Stage 2 – Funding Match
    # ------------------------------------------------------------------
    def run_funding_match(
        self,
        user: UserProfile,
        project_payload: Mapping[str, Any],
        top_k: int = 5,
    ) -> List[Match]:
        """Rank grants for the richer project payload with explanations."""

        project = ProjectProfile(
            user=user,
            description=project_payload.get("project_description", ""),
            capex=_coerce_to_float(project_payload.get("capex")),
            opex=_coerce_to_float(project_payload.get("opex")),
            timeline=project_payload.get("timeline"),
            co2e_reduction=_coerce_to_float(project_payload.get("co2_reduction")),
            partners=project_payload.get("partners"),
        )
        self.session.add(project)
        self.session.flush()

        grants = self.session.query(Grant).all()
        match_inputs: List[str] = []
        grant_refs: List[Grant] = []
        eligibility_cache: Dict[int, List[RuleEvaluation]] = {}
        user_context = {
            "industry": user.industry,
            "entity_type": user.entity_type,
            "location": user.location,
            "company_size": user.company_size,
            "project_type": user.project_type,
            "budget_min": user.budget_min,
            "budget_max": user.budget_max,
        }
        for grant in grants:
            evaluations = self._evaluate_grant_rules(
                grant,
                {**project_payload, **user_context},
            )
            eligibility_cache[grant.id] = evaluations
            match_inputs.append(self._build_grant_document(grant))
            grant_refs.append(grant)

        user_document = self._build_user_document(user, project)
        if not match_inputs:
            return []

        embeddings = self.matching_service._encode(match_inputs + [user_document])
        if embeddings.size == 0:
            return []
        grant_embeddings = embeddings[:-1]
        user_vector = embeddings[-1].reshape(1, -1)
        scores = _cosine_similarity(grant_embeddings, user_vector)
        match_results: List[Match] = []
        for grant, similarity in zip(grant_refs, scores):
            evaluations = eligibility_cache.get(grant.id, [])
            status = self._derive_status(evaluations)
            fit_reasons = [
                {
                    "id": item.id,
                    "text": item.text,
                    "citation": item.citation,
                }
                for item in evaluations
                if item.passed and item.category in {"eligibility", "fit"}
            ]
            blockers = [
                {
                    "id": item.id,
                    "text": item.text,
                    "citation": item.citation,
                }
                for item in evaluations
                if not item.passed
            ]

            rag_results = self.rag_engine.search(
                query=project_payload.get("project_description", ""),
                grant_reference=grant,
                top_k=3,
            )
            citations = [chunk for chunk in rag_results]

            match = Match(
                user=user,
                grant=grant,
                score=float(max(0.0, min(1.0, similarity)) * 100.0),
                reasons=fit_reasons,
                blockers=blockers,
                citations=citations,
                status="eligible" if status != "No" else "blocked",
                insights={
                    "max_support": grant.max_support,
                    "support_unit": grant.support_unit,
                    "deadline": grant.deadline,
                },
            )
            self.session.add(match)
            match_results.append(match)

        match_results.sort(key=lambda item: item.score, reverse=True)
        self.session.commit()
        return match_results[:top_k]

    # ------------------------------------------------------------------
    # Stage 3 – Gap-to-Yes Planner
    # ------------------------------------------------------------------
    def build_gap_plan(
        self,
        match: Match,
        assignments: Mapping[str, Any],
        default_owner: Optional[str] = None,
        default_due_in_days: int = 14,
    ) -> List[RemediationTask]:
        tasks: List[RemediationTask] = []
        due_date = date.today() + timedelta(days=default_due_in_days)
        for blocker in match.blockers:
            rule_id = blocker.get("id")
            task = RemediationTask(
                match=match,
                title=blocker.get("text", "Review blocker"),
                owner=assignments.get(rule_id, default_owner),
                due_date=due_date,
                citation=blocker.get("citation", {}),
                rule_id=rule_id,
            )
            self.session.add(task)
            tasks.append(task)
        self.session.commit()
        return tasks

    # ------------------------------------------------------------------
    # Stage 4 – Application Builder
    # ------------------------------------------------------------------
    def generate_application_sections(
        self,
        match: Match,
        requested_sections: Sequence[str] | None = None,
    ) -> List[ApplicationSection]:
        grant = match.grant
        user = match.user
        project = self.session.query(ProjectProfile).filter_by(user_id=user.id).order_by(ProjectProfile.created_at.desc()).first()
        if not project:
            raise ValueError("No project profile available for application drafting")

        sections: List[ApplicationSection] = []
        selected_sections = (
            [section for section in APPLICATION_SECTIONS if section["key"] in requested_sections]
            if requested_sections
            else APPLICATION_SECTIONS
        )

        for section_meta in selected_sections:
            key = section_meta["key"]
            title = section_meta["title"]
            query = f"{title} for {grant.title} {project.description}"
            rag_chunks = self.rag_engine.search(query=query, grant_reference=grant, top_k=3)
            assumptions = [
                f"Based on {chunk['citation'].get('title')} section {chunk['citation'].get('section')}"
                for chunk in rag_chunks
            ]
            draft = self._compose_draft_text(section_key=key, grant=grant, project=project, match=match)
            section = ApplicationSection(
                match=match,
                grant=grant,
                key=key,
                title=title,
                draft=draft,
                assumptions=assumptions,
                citations=rag_chunks,
                compliance=self._section_compliance_snapshot(key, grant),
                status="suggested",
            )
            self.session.add(section)
            sections.append(section)

        self.session.commit()
        return sections

    # ------------------------------------------------------------------
    # Stage 5 – Evidence AutoCheck
    # ------------------------------------------------------------------
    def evaluate_evidence(
        self,
        match: Match,
        documents: Sequence[Mapping[str, Any]],
    ) -> List[EvidenceRequirementStatus]:
        results: List[EvidenceRequirementStatus] = []
        provided_types = {doc.get("requirement"): doc for doc in documents}
        for requirement in match.grant.proprietary_notes or []:
            if requirement.get("category") != "evidence":
                continue
            status_value = "compliant" if requirement.get("id") in provided_types else "missing"
            notes = None
            if status_value == "missing":
                notes = f"Upload document fulfilling requirement {requirement.get('id')}"
            record = EvidenceRequirementStatus(
                user=match.user,
                grant=match.grant,
                requirement=requirement.get("text", "Evidence item"),
                status=status_value,
                notes=notes,
                citation=requirement.get("citation", {}),
            )
            self.session.add(record)
            results.append(record)

        self.session.commit()
        return results

    # ------------------------------------------------------------------
    # Stage 6 – Deadline Radar
    # ------------------------------------------------------------------
    def sync_deadlines(
        self,
        match: Match,
        milestones: Sequence[Mapping[str, Any]] | None = None,
    ) -> List[DeadlineMilestone]:
        milestones = list(milestones or [])
        results: List[DeadlineMilestone] = []
        for grant_deadline in match.grant.deadlines or []:
            due = self._parse_date(grant_deadline.get("due"))
            if due is None:
                continue
            milestone = DeadlineMilestone(
                user=match.user,
                grant=match.grant,
                label=grant_deadline.get("label", "Grant deadline"),
                due_date=due,
                is_grant_deadline=True,
                source=grant_deadline.get("source"),
            )
            self.session.add(milestone)
            results.append(milestone)

        for user_milestone in milestones:
            due = self._parse_date(user_milestone.get("due"))
            if due is None:
                continue
            milestone = DeadlineMilestone(
                user=match.user,
                grant=match.grant,
                label=user_milestone.get("label", "Milestone"),
                due_date=due,
                is_grant_deadline=False,
                source=user_milestone.get("source"),
            )
            self.session.add(milestone)
            results.append(milestone)

        self.session.commit()
        return results

    # ------------------------------------------------------------------
    # Stage 7 – Finalisation & Export readiness snapshot
    # ------------------------------------------------------------------
    def generate_finalisation_snapshot(self, match: Match) -> Dict[str, Any]:
        tasks = [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None,
            }
            for task in match.tasks
        ]
        evidence = [
            {
                "requirement": item.requirement,
                "status": item.status,
            }
            for item in match.user.evidence
            if item.grant_id == match.grant_id
        ]
        outstanding_tasks = any(task["status"] != "done" for task in tasks)
        outstanding_evidence = any(item["status"] != "compliant" for item in evidence)
        return {
            "match_id": match.id,
            "ready_for_export": not (outstanding_tasks or outstanding_evidence),
            "tasks": tasks,
            "evidence": evidence,
        }

    # ------------------------------------------------------------------
    # Stage 8 – Post submission intelligence
    # ------------------------------------------------------------------
    def post_submission_updates(self, match: Match) -> Dict[str, Any]:
        updates = []
        for note in match.grant.proprietary_notes or []:
            if note.get("category") == "update":
                updates.append(
                    {
                        "id": note.get("id"),
                        "text": note.get("text"),
                        "citation": note.get("citation"),
                    }
                )
        return {
            "match_id": match.id,
            "grant": match.grant.title,
            "updates": updates,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _evaluate_grant_rules(
        self, grant: Grant, payload: Mapping[str, Any]
    ) -> List[RuleEvaluation]:
        evaluations: List[RuleEvaluation] = []
        payload_norm = {key: _normalize(str(value)) for key, value in payload.items() if value is not None}
        for rule in grant.rules or []:
            field = rule.get("field")
            operator = rule.get("operator", "equals")
            value = rule.get("value")
            severity = rule.get("severity", "required")
            category = rule.get("category", "eligibility")
            passed = self._apply_rule(field, operator, value, payload, payload_norm)
            evaluations.append(
                RuleEvaluation(
                    id=rule.get("id", f"{grant.id}-rule"),
                    text=rule.get("text", ""),
                    citation=rule.get("citation", {}),
                    passed=passed,
                    severity=severity,
                    category=category,
                )
            )
        return evaluations

    def _apply_rule(
        self,
        field: Optional[str],
        operator: str,
        value: Any,
        payload_raw: Mapping[str, Any],
        payload_norm: Mapping[str, str],
    ) -> bool:
        if field is None:
            return True
        raw = payload_raw.get(field)
        normalized = payload_norm.get(field)

        if operator == "equals":
            if isinstance(value, str):
                return normalized == _normalize(value)
            return raw == value
        if operator == "in":
            if raw is None:
                return False
            options = {_normalize(str(item)) for item in (value or [])}
            if isinstance(raw, (list, tuple, set)):
                return any(_normalize(str(item)) in options for item in raw)
            return normalized in options
        if operator == "any":
            options = {_normalize(str(item)) for item in (value or [])}
            if isinstance(raw, (list, tuple, set)):
                return any(_normalize(str(item)) in options for item in raw)
            tokens = set(_tokenize_keywords(str(raw)))
            return bool(tokens & options)
        if operator == "gte":
            return _coerce_to_float(raw) is not None and _coerce_to_float(raw) >= _coerce_to_float(value)
        if operator == "lte":
            return _coerce_to_float(raw) is not None and _coerce_to_float(raw) <= _coerce_to_float(value)
        if operator == "range":
            number = _coerce_to_float(raw)
            if number is None:
                return False
            minimum = _coerce_to_float(value.get("min"))
            maximum = _coerce_to_float(value.get("max"))
            if minimum is not None and number < minimum:
                return False
            if maximum is not None and number > maximum:
                return False
            return True
        if operator == "contains":
            tokens = set(_tokenize_keywords(str(raw)))
            targets = {_normalize(str(item)) for item in (value or [])}
            return bool(tokens & targets)
        return True

    def _derive_status(self, evaluations: Iterable[RuleEvaluation]) -> str:
        status = "Yes"
        for item in evaluations:
            if item.passed:
                continue
            if item.severity == "required":
                return "No"
            status = "Maybe"
        return status

    def _build_user_document(self, user: UserProfile, project: ProjectProfile) -> str:
        parts = [
            user.organization or user.name,
            user.industry or "",
            user.project_type or "",
            project.description,
            project.partners or "",
        ]
        return "\n".join(part for part in parts if part)

    def _build_grant_document(self, grant: Grant) -> str:
        parts = [grant.title, grant.description]
        for rule in grant.rules or []:
            parts.append(rule.get("text", ""))
        for note in grant.proprietary_notes or []:
            parts.append(note.get("text", ""))
        return "\n".join(part for part in parts if part)

    def _compose_draft_text(
        self,
        section_key: str,
        grant: Grant,
        project: ProjectProfile,
        match: Match,
    ) -> str:
        base = f"{grant.title} expects applicants to demonstrate alignment with {grant.description[:120]}"
        if section_key == "summary":
            return (
                f"{project.description} led by {match.user.organization or match.user.name} targets {grant.title}. "
                f"The initiative invests CAPEX of {project.capex or 'N/A'} and anticipates CO2e reductions of {project.co2e_reduction or 'N/A'} t/yr."
            )
        if section_key == "objectives":
            return (
                f"Objectives focus on {match.user.focus_areas or match.user.goals or 'decarbonisation'}. "
                f"Key partners: {project.partners or 'not yet defined'}."
            )
        if section_key == "climate_impact":
            return (
                f"Projected CO2e reduction: {project.co2e_reduction or 'data pending'} tonnes annually, "
                f"supporting {grant.title}'s requirement to prioritise high-impact mitigation projects."
            )
        if section_key == "budget":
            return (
                f"CAPEX: {project.capex or 'n/a'} SEK, OPEX: {project.opex or 'n/a'} SEK with grant support ceiling {grant.max_support or 'unknown'} {grant.support_unit or ''}."
            )
        if section_key == "risk":
            return "Risks include permitting and supply lead-times; mitigation leverages municipal coordination and vetted suppliers."
        return base

    def _section_compliance_snapshot(self, section_key: str, grant: Grant) -> Dict[str, Any]:
        compliance_items = []
        for rule in grant.rules or []:
            if rule.get("category") == section_key:
                compliance_items.append(
                    {
                        "rule_id": rule.get("id"),
                        "text": rule.get("text"),
                        "citation": rule.get("citation"),
                    }
                )
        return {
            "section": section_key,
            "rules": compliance_items,
        }

    def _parse_date(self, value: Any) -> Optional[date]:
        if not value:
            return None
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except Exception:
            return None
