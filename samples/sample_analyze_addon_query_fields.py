"""Sample: analyze a document with the query fields add-on feature enabled."""
from __future__ import annotations

import argparse

from azure.ai.documentintelligence.models import DocumentAnalysisFeature

from common import (
    DEFAULT_MODEL_ID,
    build_analyze_request,
    build_client,
    format_field_value,
    format_polygon,
)


DEFAULT_QUERIES = [
    "What is the invoice number?",
    "What is the invoice date?",
    "What is the total amount due?",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a document using query fields and print the extracted answers."
    )
    parser.add_argument("document", help="Path to a local file or a publicly accessible URL to analyze.")
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Model ID to use (defaults to 'prebuilt-layout').",
    )
    parser.add_argument(
        "--query",
        dest="queries",
        action="append",
        help="Query to ask the document. Specify multiple --query arguments to run several queries.",
    )
    return parser.parse_args()


def describe_fields(result, document) -> None:
    if not document.fields:
        print("  No fields were returned for this document.")
        return

    for name, field in document.fields.items():
        value = format_field_value(field, content=result.content)
        confidence = f"{field.confidence:.2f}" if field.confidence is not None else "n/a"
        print(f"  {name}: {value} (type={field.type}, confidence={confidence})")
        if field.bounding_regions:
            for region in field.bounding_regions:
                print(
                    "    "
                    + f"Page {region.page_number} location: {format_polygon(region.polygon)}"
                )


def main() -> None:
    args = parse_args()
    queries = args.queries or DEFAULT_QUERIES

    client = build_client()
    request = build_analyze_request(args.document)

    poller = client.begin_analyze_document(
        args.model_id,
        request,
        features=[DocumentAnalysisFeature.QUERY_FIELDS],
        query_fields=queries,
    )
    result = poller.result()

    if not result.documents:
        print("No document-level fields were returned. Try a model that supports query fields, such as prebuilt-invoice.")
        return

    print(
        f"Analysis completed with model '{result.model_id}'. "
        f"Received {len(result.documents)} document(s) containing query answers.\n"
    )

    for index, document in enumerate(result.documents, start=1):
        confidence = f"{document.confidence:.2f}" if document.confidence is not None else "n/a"
        print(f"Document #{index} type={document.doc_type} confidence={confidence}")
        describe_fields(result, document)
        print()

    print("Queries executed:")
    for query in queries:
        print(f"  - {query}")


if __name__ == "__main__":
    main()
