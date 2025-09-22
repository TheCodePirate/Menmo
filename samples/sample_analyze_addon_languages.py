"""Sample: analyze a document with the language detection add-on feature enabled."""
from __future__ import annotations

import argparse

from azure.ai.documentintelligence.models import DocumentAnalysisFeature

from common import (
    DEFAULT_MODEL_ID,
    build_analyze_request,
    build_client,
    get_text_from_spans,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a document and print detected languages with confidence scores."
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
        features=[DocumentAnalysisFeature.LANGUAGES],
    )
    result = poller.result()

    languages = result.languages or []
    if not languages:
        print("No languages were detected. Provide a document that contains textual content.")
        return

    print(f"Analysis completed with model '{result.model_id}'. {len(languages)} language spans detected.\n")

    for language in languages:
        snippet = get_text_from_spans(result.content, language.spans)
        confidence = f"{language.confidence:.2f}" if language.confidence is not None else "n/a"
        print(f"Locale: {language.locale} | Confidence: {confidence}")
        if snippet:
            print(f"  Sample text: {snippet.strip()}")


if __name__ == "__main__":
    main()
