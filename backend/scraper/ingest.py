"""Command-line helpers for scraping and persisting grant data."""
from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from ..db import engine, session_scope
from ..models import Base, Grant
from .ckan import CKANScraper, CKANSourceConfig, ScrapedGrantRecord

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SCRAPED_GRANTS_PATH = DATA_DIR / "scraped_grants.json"
SCRAPED_DOCUMENTS_PATH = DATA_DIR / "scraped_documents.json"


DEFAULT_SOURCES: Sequence[CKANSourceConfig] = (
    CKANSourceConfig(
        name="California Open Data Portal",
        base_url="https://data.ca.gov",
        query="climate grant",
        jurisdiction="California",
        default_entity_types=("municipality", "nonprofit", "business"),
        default_project_types=("climate resilience", "sustainability"),
        limit=30,
    ),
    CKANSourceConfig(
        name="Data.gov",
        base_url="https://catalog.data.gov",
        query="climate grant",
        jurisdiction="United States",
        default_entity_types=("municipality", "nonprofit", "business"),
        default_project_types=("energy efficiency", "climate innovation"),
        limit=30,
    ),
)


def scrape_and_persist_grants(sources: Sequence[CKANSourceConfig] = DEFAULT_SOURCES) -> List[ScrapedGrantRecord]:
    """Fetch grant records from configured sources and persist them."""

    scraper = CKANScraper()
    try:
        records: List[ScrapedGrantRecord] = []
        for source in sources:
            fetched = scraper.fetch(source)
            logger.info("Fetched %s records from %s", len(fetched), source.name)
            records.extend(fetched)
    finally:
        scraper.close()

    if not records:
        logger.warning("No grant records fetched from configured sources")
        return []

    deduped = _deduplicate(records)
    Base.metadata.create_all(bind=engine)
    with session_scope() as session:
        for record in deduped:
            existing = session.query(Grant).filter_by(external_id=record.external_id).one_or_none()
            if existing is None:
                grant = Grant(
                    external_id=record.external_id,
                    title=record.title,
                    description=record.description,
                    sponsor=record.sponsor,
                    deadline=record.deadline,
                    url=record.url,
                    jurisdiction=record.jurisdiction,
                    source=record.source,
                    entity_types=record.entity_types,
                    industries=record.industries,
                    project_types=record.project_types,
                    budget_min=None,
                    budget_max=None,
                    min_co2_reduction=None,
                    max_support=None,
                    support_unit=None,
                    rules=[],
                    proprietary_notes=[
                        {
                            "type": "source",
                            "source": record.source,
                            "url": record.url,
                        }
                    ],
                    deadlines=[
                        {
                            "label": "submission",
                            "due": record.deadline,
                        }
                    ]
                    if record.deadline
                    else [],
                )
                session.add(grant)
            else:
                existing.title = record.title
                existing.description = record.description
                existing.sponsor = record.sponsor
                existing.deadline = record.deadline
                existing.url = record.url
                existing.jurisdiction = record.jurisdiction
                existing.source = record.source
                existing.entity_types = record.entity_types
                existing.industries = record.industries
                existing.project_types = record.project_types
                existing.deadlines = (
                    [
                        {
                            "label": "submission",
                            "due": record.deadline,
                        }
                    ]
                    if record.deadline
                    else []
                )
                existing.proprietary_notes = [
                    {
                        "type": "source",
                        "source": record.source,
                        "url": record.url,
                    }
                ]
    _write_snapshot(deduped)
    _write_documents(deduped)
    return deduped


def _deduplicate(records: Iterable[ScrapedGrantRecord]) -> List[ScrapedGrantRecord]:
    unique: Dict[str, ScrapedGrantRecord] = {}
    for record in records:
        unique[record.external_id] = record
    return list(unique.values())


def _write_snapshot(records: Sequence[ScrapedGrantRecord]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "records": [asdict(record) for record in records],
    }
    SCRAPED_GRANTS_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _write_documents(records: Sequence[ScrapedGrantRecord]) -> None:
    documents = []
    for record in records:
        if not record.notes:
            continue
        documents.append(
            {
                "id": f"scraped_{_slugify(record.external_id)}",
                "title": record.title,
                "content": record.notes,
                "citation": {
                    "title": record.source,
                    "url": record.url,
                },
                "grant_slugs": [_slugify(record.title)],
                "proprietary": False,
            }
        )
    SCRAPED_DOCUMENTS_PATH.write_text(json.dumps({"documents": documents}, indent=2, sort_keys=True))


def _slugify(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape external grant sources")
    parser.add_argument(
        "--skip-persist",
        action="store_true",
        help="Only write JSON outputs without updating the database",
    )
    args = parser.parse_args()

    if args.skip_persist:
        records = []
        scraper = CKANScraper()
        try:
            for source in DEFAULT_SOURCES:
                records.extend(scraper.fetch(source))
        finally:
            scraper.close()
        records = _deduplicate(records)
        _write_snapshot(records)
        _write_documents(records)
    else:
        scrape_and_persist_grants()


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    logging.basicConfig(level=logging.INFO)
    main()
