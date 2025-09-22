"""Helper utilities shared by the Document Intelligence add-on samples."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional, Sequence

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    DocumentField,
    DocumentSpan,
)
from azure.core.credentials import AzureKeyCredential

ENV_ENDPOINT = "DOCUMENTINTELLIGENCE_ENDPOINT"
ENV_KEY = "DOCUMENTINTELLIGENCE_KEY"
DEFAULT_MODEL_ID = "prebuilt-layout"


def build_client() -> DocumentIntelligenceClient:
    """Create a :class:`~DocumentIntelligenceClient` using environment variables."""
    endpoint = os.environ.get(ENV_ENDPOINT)
    key = os.environ.get(ENV_KEY)
    if not endpoint or not key:
        raise RuntimeError(
            "Set the DOCUMENTINTELLIGENCE_ENDPOINT and DOCUMENTINTELLIGENCE_KEY "
            "environment variables before running this sample."
        )

    return DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))


def build_analyze_request(source: str) -> AnalyzeDocumentRequest:
    """Build an :class:`AnalyzeDocumentRequest` for a local file path or URL."""
    if source.lower().startswith(("http://", "https://")):
        return AnalyzeDocumentRequest(url_source=source)

    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"Could not find document at '{source}'.")

    return AnalyzeDocumentRequest(bytes_source=path.read_bytes())


def format_polygon(polygon: Optional[Sequence[float]]) -> str:
    """Return a readable representation of a polygon."""
    if not polygon:
        return "[]"

    points = []
    for index in range(0, len(polygon), 2):
        x = polygon[index]
        y = polygon[index + 1]
        points.append(f"({x:.2f}, {y:.2f})")
    return "[" + ", ".join(points) + "]"


def get_text_from_spans(content: str, spans: Optional[Iterable[DocumentSpan]]) -> str:
    """Extract the text covered by the provided spans."""
    if not content or not spans:
        return ""

    segments: list[str] = []
    for span in spans:
        if span.length:
            segments.append(content[span.offset : span.offset + span.length])
    return "".join(segments)


def format_field_value(field: DocumentField, *, content: Optional[str] = None) -> str:
    """Create a readable string representation of a :class:`DocumentField`."""
    if field is None:
        return ""

    simple_attrs = (
        "value_string",
        "value_date",
        "value_time",
        "value_phone_number",
        "value_number",
        "value_integer",
        "value_boolean",
        "value_country_region",
    )
    for attr in simple_attrs:
        value = getattr(field, attr, None)
        if value is not None:
            return str(value)

    if field.type == "currency" and field.value_currency:
        currency = field.value_currency
        amount = currency.amount
        if amount is None:
            return ""
        if currency.currency_symbol:
            return f"{currency.currency_symbol}{amount}"
        if currency.currency_code:
            return f"{amount} {currency.currency_code}"
        return str(amount)

    if field.type == "address" and field.value_address:
        address = field.value_address
        components = [
            address.street_address,
            address.city,
            address.state,
            address.postal_code,
            address.country_region,
        ]
        return ", ".join([component for component in components if component])

    if field.type == "array" and field.value_array:
        return "[" + ", ".join(format_field_value(item, content=content) for item in field.value_array) + "]"

    if field.type == "object" and field.value_object:
        return "{ " + ", ".join(
            f"{name}: {format_field_value(value, content=content)}" for name, value in field.value_object.items()
        ) + " }"

    if field.type == "selectionMark" and field.value_selection_mark:
        return field.value_selection_mark

    if field.type == "signature" and field.value_signature:
        return field.value_signature

    if field.type == "selectionGroup" and field.value_selection_group:
        return "[" + ", ".join(field.value_selection_group) + "]"

    if field.content:
        return field.content.strip()

    if content and field.spans:
        text = get_text_from_spans(content, field.spans).strip()
        if text:
            return text

    return ""


__all__ = [
    "DEFAULT_MODEL_ID",
    "build_analyze_request",
    "build_client",
    "format_field_value",
    "format_polygon",
    "get_text_from_spans",
]
