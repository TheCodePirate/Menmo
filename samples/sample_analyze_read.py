"""Sample script to analyze printed and handwritten text using Azure Document Intelligence."""
import argparse
import os
from typing import Iterable
from urllib.parse import urlparse

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential


ENV_ENDPOINT = "AZURE_DOCUMENTINTELLIGENCE_ENDPOINT"
ENV_KEY = "AZURE_DOCUMENTINTELLIGENCE_KEY"


def _is_url(source: str) -> bool:
    try:
        parsed = urlparse(source)
    except Exception:
        return False
    return all([parsed.scheme in {"http", "https"}, parsed.netloc])


def _print_lines(header: str, lines: Iterable[str]) -> None:
    print(header)
    for line in lines:
        print(f"  - {line}")
    if not lines:
        print("  (none)")


def main(document_source: str) -> None:
    """Analyze the supplied document and print printed and handwritten text."""

    try:
        endpoint = os.environ[ENV_ENDPOINT]
        key = os.environ[ENV_KEY]
    except KeyError as exc:
        missing = exc.args[0]
        raise RuntimeError(
            f"Missing required environment variable: {missing}. "
            f"Please set {ENV_ENDPOINT} and {ENV_KEY}."
        ) from exc

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    if _is_url(document_source):
        poller = client.begin_analyze_document(
            model_id="prebuilt-read", analyze_request={"urlSource": document_source}
        )
    else:
        with open(document_source, "rb") as document_file:
            poller = client.begin_analyze_document("prebuilt-read", document=document_file)

    result = poller.result()

    printed_lines = []
    handwritten_lines = []

    for page in getattr(result, "pages", []):
        for line in getattr(page, "lines", []) or []:
            style_name = None
            if getattr(line, "appearance", None) is not None:
                style_name = getattr(line.appearance, "style_name", None)
            if style_name == "handwriting":
                handwritten_lines.append(line.content)
            else:
                printed_lines.append(line.content)

    _print_lines("Printed text lines:", printed_lines)
    _print_lines("Handwritten text lines:", handwritten_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a document with the Azure Document Intelligence prebuilt Read model and "
            "print extracted printed and handwritten text lines."
        )
    )
    parser.add_argument(
        "document",
        help=(
            "Path to a local file or URL pointing to the document to analyze. "
            "The script expects the Azure Document Intelligence endpoint and key to be set "
            f"in the {ENV_ENDPOINT} and {ENV_KEY} environment variables."
        ),
    )
    args = parser.parse_args()

    main(args.document)
