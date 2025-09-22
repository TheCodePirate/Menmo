"""Sample: analyze a document with the font style add-on feature enabled."""
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
        description="Analyze a document and inspect detected font styles using Azure Document Intelligence."
    )
    parser.add_argument("document", help="Path to a local file or a publicly accessible URL to analyze.")
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Model ID to use (defaults to 'prebuilt-layout').",
    )
    return parser.parse_args()


def describe_style(style, content: str) -> None:
    text = get_text_from_spans(content, style.spans)
    print("- Detected style:")
    print(f"    Similar font family: {style.similar_font_family or 'unknown'}")
    if style.font_style:
        print(f"    Font style: {style.font_style}")
    if style.font_weight:
        print(f"    Font weight: {style.font_weight}")
    if style.is_handwritten is None:
        handwritten = "unknown"
    else:
        handwritten = "yes" if style.is_handwritten else "no"
    print(f"    Handwritten: {handwritten}")
    if style.color or style.background_color:
        print(f"    Text color: {style.color or 'n/a'} | Background color: {style.background_color or 'n/a'}")
    confidence = f"{style.confidence:.2f}" if style.confidence is not None else "n/a"
    print(f"    Confidence: {confidence}")
    snippet = text.strip()
    if snippet:
        print(f"    Sample text: {snippet}")


def main() -> None:
    args = parse_args()
    client = build_client()
    request = build_analyze_request(args.document)

    poller = client.begin_analyze_document(
        args.model_id,
        request,
        features=[DocumentAnalysisFeature.STYLE_FONT],
    )
    result = poller.result()

    styles = result.styles or []
    if not styles:
        print("No font styles were returned. Ensure the analyzed document contains text.")
        return

    print(f"Analysis completed with model '{result.model_id}'. {len(styles)} styles detected.\n")

    for style in styles:
        describe_style(style, result.content)


if __name__ == "__main__":
    main()
