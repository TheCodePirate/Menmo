"""Sample: analyze a document with the high-resolution OCR add-on feature enabled."""
from __future__ import annotations

import argparse

from azure.ai.documentintelligence.models import DocumentAnalysisFeature

from common import (
    DEFAULT_MODEL_ID,
    build_analyze_request,
    build_client,
    format_polygon,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a document and display high-resolution word bounding boxes."
    )
    parser.add_argument("document", help="Path to a local file or a publicly accessible URL to analyze.")
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Model ID to use (defaults to 'prebuilt-layout').",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=20,
        help="Maximum number of word bounding boxes to print per page (default: 20).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = build_client()
    request = build_analyze_request(args.document)

    poller = client.begin_analyze_document(
        args.model_id,
        request,
        features=[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION],
    )
    result = poller.result()

    print(f"Analysis completed with model '{result.model_id}' (API version {result.api_version}).")

    for page in result.pages:
        words = page.words or []
        if not words:
            print(f"\nPage {page.page_number} did not return any words.")
            continue

        print(
            f"\nPage {page.page_number} - size: {page.width}x{page.height} {page.unit or ''} | displaying up to {args.max_words} words"
        )
        for word in words[: args.max_words]:
            confidence = f"{word.confidence:.2f}" if word.confidence is not None else "n/a"
            print(f"  '{word.content}' -> {format_polygon(word.polygon)} (confidence {confidence})")

        if len(words) > args.max_words:
            print(f"  ... {len(words) - args.max_words} additional words omitted for brevity ...")


if __name__ == "__main__":
    main()
