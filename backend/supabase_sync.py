"""Utility helpers for synchronising Menmo data with Supabase."""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from sqlalchemy.orm import Session

try:  # pragma: no cover - optional dependency
    from supabase import Client, create_client
except Exception:  # pragma: no cover - import guard for optional dependency
    Client = None  # type: ignore[assignment]
    create_client = None  # type: ignore[assignment]

from .models import Match, RemediationTask

LOGGER = logging.getLogger(__name__)


def _default_json(value: Any) -> Any:
    """Return objects that can be serialised by Supabase."""

    if isinstance(value, (str, int, float)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_default_json(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _default_json(item) for key, item in value.items()}
    # Fall back to string representation for SQLAlchemy rows/dates etc.
    return json.loads(json.dumps(value, default=str))


class SupabaseSync:
    """Facade handling best-effort replication of entities to Supabase tables."""

    def __init__(
        self,
        client: Optional[Client],
        match_table: str = "matches",
        task_table: str = "remediation_tasks",
    ) -> None:
        self._client = client
        self.match_table = match_table
        self.task_table = task_table

    @classmethod
    def from_env(cls) -> "SupabaseSync":
        """Factory that instantiates a Supabase client when env variables exist."""

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        match_table = os.getenv("SUPABASE_MATCH_TABLE", "matches")
        task_table = os.getenv("SUPABASE_TASK_TABLE", "remediation_tasks")
        if not url or not key or create_client is None:
            if url or key:
                LOGGER.warning(
                    "Supabase credentials incomplete; skipping Supabase integration."
                )
            return cls(client=None, match_table=match_table, task_table=task_table)

        try:
            client = create_client(url, key)  # type: ignore[misc]
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.warning("Failed to initialise Supabase client: %s", exc)
            client = None
        return cls(client=client, match_table=match_table, task_table=task_table)

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def sync_matches(self, matches: Iterable[Match]) -> None:
        """Upsert match payloads into Supabase."""

        if not self.enabled:
            return
        payloads: List[MutableMapping[str, Any]] = []
        for match in matches:
            payloads.append(
                {
                    "id": match.id,
                    "user_id": match.user_id,
                    "grant_id": match.grant_id,
                    "score": match.score,
                    "status": match.status,
                    "reasons": _default_json(match.reasons),
                    "blockers": _default_json(match.blockers),
                    "citations": _default_json(match.citations),
                    "insights": _default_json(match.insights),
                    "created_at": match.created_at,
                    "updated_at": match.updated_at,
                }
            )

        if not payloads:
            return
        try:
            self._client.table(self.match_table).upsert(payloads).execute()  # type: ignore[union-attr]
        except Exception as exc:  # pragma: no cover - external service failures
            LOGGER.warning("Supabase match upsert failed: %s", exc)

    def sync_tasks(self, tasks: Iterable[RemediationTask]) -> None:
        """Upsert task payloads into Supabase."""

        if not self.enabled:
            return
        payloads: List[MutableMapping[str, Any]] = []
        for task in tasks:
            payloads.append(
                {
                    "id": task.id,
                    "match_id": task.match_id,
                    "title": task.title,
                    "status": task.status,
                    "owner": task.owner,
                    "due_date": task.due_date,
                    "citation": _default_json(task.citation),
                    "rule_id": task.rule_id,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                }
            )

        if not payloads:
            return
        try:
            self._client.table(self.task_table).upsert(payloads).execute()  # type: ignore[union-attr]
        except Exception as exc:  # pragma: no cover - external service failures
            LOGGER.warning("Supabase task upsert failed: %s", exc)

    def sync_session(self, session: Session) -> None:
        """Flush a session and sync outstanding entities in a single call."""

        if not self.enabled:
            return
        session.flush()
        matches = session.query(Match).all()
        tasks = session.query(RemediationTask).all()
        self.sync_matches(matches)
        self.sync_tasks(tasks)
