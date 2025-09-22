"""Sample: analyze a document with the barcodes add-on feature enabled."""
from __future__ import annotations

import argparse

from azure.ai.documentintelligence.models import DocumentAnalysisFeature

from common import (
    DEFAULT_MODEL_ID,
    build_analyze_request,
    build_client,
    format_polygon,
    get_text_from_spans,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a document and extract barcode values using Azure Document Intelligence."
    )
    parser.add_argument("document", help="Path to a local file or a publicly accessible URL to analyze.")
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Model ID to use (defaults to 'prebuilt-layout').",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = build_client()
    request = build_analyze_request(args.document)

    poller = client.begin_analyze_document(
        args.model_id,
        request,
        features=[DocumentAnalysisFeature.BARCODES],
    )
    result = poller.result()

    print(f"Analysis completed with model '{result.model_id}' (API version {result.api_version}).")

    any_barcodes = False
    for page in result.pages:
        if not page.barcodes:
            continue

        any_barcodes = True
        print(f"\nPage {page.page_number} barcodes (unit: {page.unit or 'unspecified'}):")
        for index, barcode in enumerate(page.barcodes, start=1):
            snippet = get_text_from_spans(result.content, [barcode.span]) if barcode.span else ""
            confidence = f"{barcode.confidence:.2f}" if barcode.confidence is not None else "n/a"
            print(f"  Barcode #{index} kind={barcode.kind} value='{barcode.value}' confidence={confidence}")
            if snippet:
                print(f"    Text span snippet: {snippet}")
            print(f"    Polygon: {format_polygon(barcode.polygon)}")

    if not any_barcodes:
        print("\nNo barcodes were detected in the analyzed document.")


if __name__ == "__main__":
    main()
