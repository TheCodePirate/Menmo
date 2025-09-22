"""Analyze identity documents with the prebuilt model."""
from __future__ import annotations

import argparse
from typing import Optional

from azure.ai.documentintelligence.models import AnalyzedDocument, DocumentField

from _helpers import (
    add_common_arguments,
    analyze_document,
    create_client,
    value_with_confidence,
)

MODEL_ID = "prebuilt-idDocument"


def print_field(label: str, field: Optional[DocumentField], indent: int = 4) -> None:
    value, confidence = value_with_confidence(field)
    prefix = " " * indent + f"{label}: "
    if value is None or value == "":
        print(prefix + "--")
        return
    text = value
    if confidence:
        text += f" (confidence: {confidence})"
    print(prefix + text)


def describe_identity_document(document: AnalyzedDocument, index: int) -> None:
    print(f"-------- Identity document #{index} ({document.doc_type or 'idDocument'}) --------")
    fields = document.fields or {}
    print("  Person details")
    print_field("First name", fields.get("FirstName"))
    print_field("Last name", fields.get("LastName"))
    print_field("Full name", fields.get("FullName"))
    print_field("Sex", fields.get("Sex"))
    print_field("Date of birth", fields.get("DateOfBirth"))
    print_field("Date of expiration", fields.get("DateOfExpiration"))
    print_field("Date of issue", fields.get("DateOfIssue"))
    print("  Document information")
    print_field("Document number", fields.get("DocumentNumber"))
    print_field("Document type", fields.get("DocumentType"))
    print_field("Country/Region", fields.get("CountryRegion"))
    print_field("Nationality", fields.get("Nationality"))
    print_field("Region", fields.get("Region"))
    print_field("Authority", fields.get("Authority"))
    print("  Contact details")
    print_field("Address", fields.get("Address"))
    print_field("Residence", fields.get("Residence"))


def main() -> None:
    parser = add_common_arguments(argparse.ArgumentParser(description="Analyze identity documents."))
    args = parser.parse_args()

    client = create_client(args.endpoint, args.key)
    result = analyze_document(
        client,
        MODEL_ID,
        args.document,
        locale=args.locale,
        pages=args.pages,
    )

    documents = getattr(result, "documents", [])
    if not documents:
        print("No identity documents were returned.")
        return

    for index, analyzed in enumerate(documents, start=1):
        describe_identity_document(analyzed, index)


if __name__ == "__main__":
    main()
