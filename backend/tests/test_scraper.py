"""Tests for the grant scraping helpers."""
from __future__ import annotations

import httpx

from backend.scraper.ckan import CKANScraper, CKANSourceConfig, ScrapedGrantRecord
from backend.scraper.ingest import _deduplicate, _slugify


def _build_dataset() -> dict:
    return {
        "id": "dataset-123",
        "title": "Climate Resilience Grant Program",
        "notes": "<p>Provides funding for community-led <strong>climate</strong> projects.</p>",
        "organization": {"title": "Department of Sustainability"},
        "url": "https://example.org/datasets/climate",
        "tags": [
            {"name": "climate"},
            {"display_name": "resilience"},
        ],
        "resources": [
            {"url": "https://example.org/datasets/climate/resource"},
        ],
        "temporal": "2019-01-01/2020-12-31",
    }


def test_normalise_dataset_extracts_metadata() -> None:
    config = CKANSourceConfig(
        name="Test Portal",
        base_url="https://example.org",
        query="climate",
        jurisdiction="Example State",
        default_entity_types=("municipality", "nonprofit"),
        default_project_types=("climate action",),
    )
    scraper = CKANScraper(client=httpx.Client())
    try:
        record = scraper._normalise_dataset(_build_dataset(), config)
    finally:
        scraper.close()

    assert isinstance(record, ScrapedGrantRecord)
    assert record.external_id == "Test Portal:dataset-123"
    assert record.description == "Provides funding for community-led climate projects."
    assert record.deadline == "2020-12-31"
    assert record.industries == ["climate", "resilience"]
    assert record.entity_types == ["municipality", "nonprofit"]
    assert record.project_types == ["climate action"]


def test_deduplicate_keeps_last_record() -> None:
    record_one = ScrapedGrantRecord(
        external_id="Test Portal:dataset-123",
        title="Original",
        description="desc",
        sponsor="Dept",
        url="https://example.org",
        jurisdiction="Example State",
        entity_types=["municipality"],
        industries=["climate"],
        project_types=["action"],
        deadline=None,
        source="Test Portal",
        notes="notes",
    )
    record_two = ScrapedGrantRecord(
        external_id="Test Portal:dataset-123",
        title="Updated",
        description="desc",
        sponsor="Dept",
        url="https://example.org",
        jurisdiction="Example State",
        entity_types=["municipality"],
        industries=["climate"],
        project_types=["action"],
        deadline=None,
        source="Test Portal",
        notes="notes",
    )

    deduped = _deduplicate([record_one, record_two])
    assert len(deduped) == 1
    assert deduped[0].title == "Updated"


def test_slugify_normalises_text() -> None:
    assert _slugify("Climate Grant 2024!") == "climategrant2024"
