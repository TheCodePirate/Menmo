"""Scraper for CKAN-powered open data portals."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from typing import Any, Dict, Iterable, List, Optional, Sequence

import httpx

logger = logging.getLogger(__name__)


@dataclass
class CKANSourceConfig:
    """Configuration for a CKAN source."""

    name: str
    base_url: str
    query: str
    jurisdiction: str
    default_entity_types: Sequence[str]
    default_project_types: Sequence[str]
    limit: int = 25
    tags_as_industries: bool = True


@dataclass
class ScrapedGrantRecord:
    """Normalised grant-like record returned by scraping."""

    external_id: str
    title: str
    description: str
    sponsor: str
    url: Optional[str]
    jurisdiction: str
    entity_types: List[str]
    industries: List[str]
    project_types: List[str]
    deadline: Optional[str]
    source: str
    notes: str


class _HTMLStripper(HTMLParser):
    """Small helper to strip HTML tags."""

    def __init__(self) -> None:
        super().__init__()
        self._chunks: List[str] = []

    def handle_data(self, data: str) -> None:  # noqa: D401 - HTMLParser API
        if data:
            self._chunks.append(data)

    def get_text(self) -> str:
        return " ".join(chunk.strip() for chunk in self._chunks if chunk.strip())


class CKANScraper:
    """Collect grant-like datasets from CKAN portals."""

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        headers = {"User-Agent": "MenmoGrantScraper/1.0"}
        self._client = client or httpx.Client(timeout=30, headers=headers)

    def close(self) -> None:
        self._client.close()

    def fetch(self, config: CKANSourceConfig) -> List[ScrapedGrantRecord]:
        """Fetch and normalise datasets for a given source configuration."""

        endpoint = f"{config.base_url.rstrip('/')}/api/3/action/package_search"
        params = {"q": config.query, "rows": config.limit}
        try:
            response = self._client.get(endpoint, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network failure path
            logger.warning("Failed to fetch from %s: %s", config.name, exc)
            return []

        payload = response.json()
        if not payload.get("success"):
            logger.warning("CKAN response from %s reported failure", config.name)
            return []

        records: List[ScrapedGrantRecord] = []
        for dataset in payload.get("result", {}).get("results", []):
            normalised = self._normalise_dataset(dataset, config)
            if normalised:
                records.append(normalised)
        return records

    def _normalise_dataset(
        self, dataset: Dict[str, Any], config: CKANSourceConfig
    ) -> Optional[ScrapedGrantRecord]:
        title = dataset.get("title") or dataset.get("name")
        identifier = dataset.get("id") or dataset.get("name")
        if not title or not identifier:
            return None

        sponsor = _extract_sponsor(dataset)
        description = _strip_html(dataset.get("notes") or "")
        industries = _extract_tags(dataset) if config.tags_as_industries else []
        if not industries:
            industries = ["climate"]
        deadline = _parse_deadline(dataset)
        url = dataset.get("url") or _first_resource_url(dataset)
        notes = description or f"Dataset collected from {config.name}."

        return ScrapedGrantRecord(
            external_id=f"{config.name}:{identifier}",
            title=title.strip(),
            description=description or title.strip(),
            sponsor=sponsor,
            url=url,
            jurisdiction=config.jurisdiction,
            entity_types=list(config.default_entity_types),
            industries=industries,
            project_types=list(config.default_project_types),
            deadline=deadline,
            source=config.name,
            notes=notes,
        )


def _extract_sponsor(dataset: Dict[str, Any]) -> str:
    organization = dataset.get("organization") or {}
    if isinstance(organization, dict):
        name = organization.get("title") or organization.get("name")
        if name:
            return name
    return "Unknown"


def _strip_html(value: str) -> str:
    if not value:
        return ""
    stripper = _HTMLStripper()
    stripper.feed(value)
    return stripper.get_text()


def _extract_tags(dataset: Dict[str, Any]) -> List[str]:
    tags: Iterable[Dict[str, Any]] = dataset.get("tags") or []
    names: List[str] = []
    for tag in tags:
        name = tag.get("display_name") or tag.get("name")
        if name:
            names.append(name)
    return names


def _first_resource_url(dataset: Dict[str, Any]) -> Optional[str]:
    resources: Iterable[Dict[str, Any]] = dataset.get("resources") or []
    for resource in resources:
        url = resource.get("url")
        if url:
            return url
    return None


def _parse_deadline(dataset: Dict[str, Any]) -> Optional[str]:
    temporal = dataset.get("temporal") or _lookup_extra(dataset, "temporal")
    if not temporal:
        return None
    if isinstance(temporal, str) and "/" in temporal:
        _, _, maybe_end = temporal.partition("/")
        maybe_end = maybe_end.strip()
        if maybe_end:
            parsed = _parse_date(maybe_end)
            if parsed:
                return parsed
    parsed = _parse_date(temporal)
    return parsed


def _lookup_extra(dataset: Dict[str, Any], key: str) -> Optional[str]:
    extras: Iterable[Dict[str, Any]] = dataset.get("extras") or []
    for extra in extras:
        if extra.get("key") == key:
            return extra.get("value")
    return None


def _parse_date(value: Any) -> Optional[str]:
    if not value or not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%Y"):
        try:
            dt = datetime.strptime(value.strip(), fmt)
            if fmt == "%Y":
                dt = dt.replace(month=12, day=31)
            return dt.date().isoformat()
        except ValueError:
            continue
    return None


__all__ = [
    "CKANScraper",
    "CKANSourceConfig",
    "ScrapedGrantRecord",
]
