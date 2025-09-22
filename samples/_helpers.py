"""Shared helpers for Document Intelligence samples."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, MutableMapping, Optional, Tuple
from urllib.parse import urlparse

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AddressValue,
    AnalyzeDocumentRequest,
    CurrencyValue,
    DocumentField,
)
from azure.core.credentials import AzureKeyCredential


def add_common_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add standard CLI arguments used by the Document Intelligence samples."""
    parser.add_argument(
        "--endpoint",
        required=True,
        help="Document Intelligence endpoint, e.g. https://<resource-name>.cognitiveservices.azure.com.",
    )
    parser.add_argument("--key", required=True, help="Document Intelligence API key.")
    parser.add_argument(
        "--document",
        required=True,
        help="Path to a local document or an HTTPS/SAS URL that should be analyzed.",
    )
    parser.add_argument(
        "--locale",
        help="Optional BCP-47 language code that hints the document language (for example: en-US).",
    )
    parser.add_argument(
        "--pages",
        help="Optional comma separated list of 1-indexed pages or page ranges (for example: 1,3-5).",
    )
    return parser


def create_client(endpoint: str, key: str) -> DocumentIntelligenceClient:
    """Create a :class:`DocumentIntelligenceClient` from endpoint and key credentials."""
    return DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def _is_url(document: str) -> bool:
    parsed = urlparse(document)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _build_analyze_request(document: str) -> AnalyzeDocumentRequest:
    expanded = os.path.expanduser(document)
    file_path = Path(expanded)
    if file_path.is_file():
        data = file_path.read_bytes()
        if not data:
            raise ValueError(f"The document at '{file_path}' is empty.")
        return AnalyzeDocumentRequest(bytes_source=data)
    if _is_url(document):
        return AnalyzeDocumentRequest(url_source=document)
    raise FileNotFoundError(
        "Document source must be an existing file or an HTTPS/SAS URL. "
        f"Could not resolve '{document}'."
    )


def analyze_document(
    client: DocumentIntelligenceClient,
    model_id: str,
    document: str,
    *,
    locale: Optional[str] = None,
    pages: Optional[str] = None,
) -> MutableMapping[str, Any]:
    """Start an analysis operation and return the result."""
    request = _build_analyze_request(document)
    kwargs: Dict[str, Any] = {}
    if locale:
        kwargs["locale"] = locale
    if pages:
        kwargs["pages"] = pages
    poller = client.begin_analyze_document(model_id=model_id, body=request, **kwargs)
    return poller.result()


def format_currency_value(currency: CurrencyValue) -> str:
    amount = currency.amount
    amount_text = f"{amount:,.2f}" if amount is not None else ""
    if currency.currency_code:
        if amount_text:
            return f"{amount_text} {currency.currency_code}"
        return currency.currency_code
    if currency.currency_symbol:
        return f"{currency.currency_symbol}{amount_text}" if amount_text else currency.currency_symbol
    return amount_text


def format_address_value(address: AddressValue) -> str:
    lines: List[str] = []
    if address.street_address:
        lines.append(address.street_address)
    line_two_parts = [part for part in (address.city, address.state, address.postal_code) if part]
    if line_two_parts:
        lines.append(", ".join(line_two_parts))
    if address.country_region:
        lines.append(address.country_region)
    if not lines:
        components = [
            part
            for part in (
                address.house_number,
                address.road,
                address.city,
                address.state,
                address.postal_code,
                address.country_region,
            )
            if part
        ]
        if components:
            lines.append(", ".join(components))
    return "; ".join(lines)


def format_document_field(field: Optional[DocumentField]) -> Optional[Any]:
    if field is None:
        return None
    if field.value_currency is not None:
        return format_currency_value(field.value_currency)
    if field.value_address is not None:
        return format_address_value(field.value_address)
    if field.value_date is not None:
        return field.value_date.isoformat()
    if field.value_time is not None:
        return field.value_time.isoformat()
    if field.value_phone_number is not None:
        return field.value_phone_number
    if field.value_country_region is not None:
        return field.value_country_region
    if field.value_string is not None:
        return field.value_string
    if field.value_integer is not None:
        return field.value_integer
    if field.value_number is not None:
        return field.value_number
    if field.value_boolean is not None:
        return field.value_boolean
    if field.value_object is not None:
        return {key: format_document_field(value) for key, value in field.value_object.items()}
    if field.value_array is not None:
        return [format_document_field(item) for item in field.value_array]
    if field.content:
        return field.content.strip()
    return None


def confidence_to_str(field: Optional[DocumentField]) -> Optional[str]:
    if field is not None and field.confidence is not None:
        return f"{field.confidence:.2f}"
    return None


def value_with_confidence(
    field: Optional[DocumentField],
    formatter: Optional[Callable[[DocumentField], Any]] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Return a formatted value string and confidence for a document field."""
    if field is None:
        return None, None
    if formatter is not None:
        value = formatter(field)
    else:
        value = format_document_field(field)
        if field.value_currency is None and field.value_number is not None:
            value = f"{field.value_number:,.2f}"
        elif field.value_integer is not None:
            value = str(field.value_integer)
        elif isinstance(value, bool):
            value = "Yes" if value else "No"
    if value is not None and not isinstance(value, str):
        value = str(value)
    return value, confidence_to_str(field)
