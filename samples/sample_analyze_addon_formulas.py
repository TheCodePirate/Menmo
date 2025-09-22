"""Sample: analyze a document with the formulas add-on feature enabled."""
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
        description="Analyze a document and list detected mathematical formulas."
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
        features=[DocumentAnalysisFeature.FORMULAS],
    )
    result = poller.result()

    print(f"Analysis completed with model '{result.model_id}' (API version {result.api_version}).")

    found_any = False
    for page in result.pages:
        if not page.formulas:
            continue

        found_any = True
        print(f"\nPage {page.page_number} formulas:")
        for index, formula in enumerate(page.formulas, start=1):
            snippet = get_text_from_spans(result.content, [formula.span]) if formula.span else ""
            confidence = f"{formula.confidence:.2f}" if formula.confidence is not None else "n/a"
            print(f"  Formula #{index} kind={formula.kind} value='{formula.value}' confidence={confidence}")
            if snippet:
                print(f"    Text span snippet: {snippet}")
            print(f"    Polygon: {format_polygon(formula.polygon)}")

    if not found_any:
        print("\nNo formulas were detected in the analyzed document.")


if __name__ == "__main__":
    main()
