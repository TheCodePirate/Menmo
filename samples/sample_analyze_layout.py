"""Inspect layout information produced by Azure Document Intelligence."""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, Iterable, List, Optional, Tuple

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeResult,
    DocumentParagraph,
    DocumentSection,
    DocumentSpan,
    DocumentTable,
)
from azure.core.credentials import AzureKeyCredential


ENV_ENDPOINT = "AZURE_DOCUMENTINTELLIGENCE_ENDPOINT"
ENV_KEY = "AZURE_DOCUMENTINTELLIGENCE_KEY"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a document with the prebuilt layout model and inspect its structure.",
    )
    parser.add_argument(
        "document",
        help="Path to the input document (PDF, TIFF, JPEG, PNG, etc.) to analyze.",
    )
    return parser.parse_args()


def build_client() -> DocumentIntelligenceClient:
    endpoint = os.getenv(ENV_ENDPOINT)
    key = os.getenv(ENV_KEY)

    if not endpoint or not key:
        missing = []
        if not endpoint:
            missing.append(ENV_ENDPOINT)
        if not key:
            missing.append(ENV_KEY)
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Set the {joined} environment variable(s) with your Document Intelligence resource credentials before running the sample."
        )

    return DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def analyze_document(client: DocumentIntelligenceClient, document_path: str) -> AnalyzeResult:
    with open(document_path, "rb") as document_data:
        poller = client.begin_analyze_document("prebuilt-layout", document_data)
    return poller.result()


def print_paragraphs(result: AnalyzeResult) -> None:
    print("\nParagraphs\n---------")
    paragraphs = result.paragraphs or []
    if not paragraphs:
        print("No paragraphs detected.")
        return

    for idx, paragraph in enumerate(paragraphs, start=1):
        role = paragraph.role or "content"
        content = paragraph.content.replace("\n", " ").strip()
        print(f"{idx}. Role: {role}")
        print(f"   Text: {content}")
        if paragraph.bounding_regions:
            for region in paragraph.bounding_regions:
                polygon_pairs = [
                    f"({region.polygon[i]:.1f}, {region.polygon[i + 1]:.1f})"
                    for i in range(0, len(region.polygon), 2)
                ]
                polygon_string = " ".join(polygon_pairs)
                print(f"   Page {region.page_number} polygon: {polygon_string}")
        span_preview = _get_span_preview(result, paragraph.spans)
        if span_preview:
            print(f"   Content span preview: {span_preview}")


def print_tables(result: AnalyzeResult) -> None:
    print("\nTables\n------")
    tables = result.tables or []
    if not tables:
        print("No tables detected.")
        return

    for idx, table in enumerate(tables, start=1):
        print(f"Table {idx}: {table.row_count} x {table.column_count}")
        _print_table_structure(table)
        if table.bounding_regions:
            for region in table.bounding_regions:
                polygon_pairs = [
                    f"({region.polygon[i]:.1f}, {region.polygon[i + 1]:.1f})"
                    for i in range(0, len(region.polygon), 2)
                ]
                polygon_string = " ".join(polygon_pairs)
                print(f"  Page {region.page_number} polygon: {polygon_string}")
        span_preview = _get_span_preview(result, table.spans)
        if span_preview:
            print(f"  Content span preview: {span_preview}")


def print_sections(result: AnalyzeResult) -> None:
    print("\nSections\n--------")
    sections = result.sections or []
    if not sections:
        print("No sections detected.")
        return

    element_lookup = _build_element_lookup(result)
    child_section_indices = _collect_child_sections(sections)

    root_indices = [index for index in range(len(sections)) if index not in child_section_indices]
    if not root_indices:
        root_indices = list(range(len(sections)))

    visited: set[int] = set()

    def _print_section(index: int, depth: int) -> None:
        if index in visited:
            indent = "  " * depth
            print(f"{indent}- Section {index} (cyclic reference detected, skipping further traversal)")
            return

        visited.add(index)
        section = sections[index]
        indent = "  " * depth
        span_preview = _get_span_preview(result, section.spans)
        preview_text = span_preview or "(no text span)"
        print(f"{indent}- Section {index}: {preview_text}")
        if not section.elements:
            return

        for element_id in section.elements:
            kind, obj = element_lookup.get(element_id, (None, None))
            child_indent = "  " * (depth + 1)
            if kind == "section" and isinstance(obj, int):
                _print_section(obj, depth + 1)
            elif kind == "paragraph" and isinstance(obj, DocumentParagraph):
                role = obj.role or "content"
                preview = obj.content.replace("\n", " ").strip()
                if len(preview) > 80:
                    preview = preview[:77] + "..."
                print(f"{child_indent}- Paragraph ({role}): {preview}")
            elif kind == "table" and isinstance(obj, DocumentTable):
                print(f"{child_indent}- Table ({obj.row_count} x {obj.column_count})")
            else:
                print(f"{child_indent}- Element {element_id}")

    for root_index in root_indices:
        _print_section(root_index, 0)


def _get_span_preview(result: AnalyzeResult, spans: Optional[Iterable[DocumentSpan]]) -> Optional[str]:
    if not spans:
        return None

    snippets: List[str] = []
    for span in spans:
        start = span.offset
        end = start + span.length
        snippets.append(result.content[start:end].replace("\n", " ").strip())
    preview = " ".join(filter(None, snippets)).strip()
    if not preview:
        return None
    if len(preview) > 100:
        return preview[:97] + "..."
    return preview


def _print_table_structure(table: DocumentTable) -> None:
    cells: Dict[Tuple[int, int], Tuple[str, Optional[int], Optional[int]]] = {}
    for cell in table.cells:
        text = cell.content.replace("\n", " ").strip()
        cells[(cell.row_index, cell.column_index)] = (text, cell.row_span, cell.column_span)

    for row_index in range(table.row_count):
        row_cells: List[str] = []
        for column_index in range(table.column_count):
            text, row_span, column_span = cells.get((row_index, column_index), ("", None, None))
            annotations: List[str] = []
            if row_span and row_span > 1:
                annotations.append(f"row_span={row_span}")
            if column_span and column_span > 1:
                annotations.append(f"col_span={column_span}")
            if annotations:
                row_cells.append(f"{text} ({', '.join(annotations)})")
            else:
                row_cells.append(text)
        print("  | " + " | ".join(row_cells) + " |")


def _build_element_lookup(result: AnalyzeResult) -> Dict[str, Tuple[str, object]]:
    lookup: Dict[str, Tuple[str, object]] = {}

    for index, paragraph in enumerate(result.paragraphs or []):
        lookup[f"#/paragraphs/{index}"] = ("paragraph", paragraph)
    for index, table in enumerate(result.tables or []):
        lookup[f"#/tables/{index}"] = ("table", table)
    for index, section in enumerate(result.sections or []):
        lookup[f"#/sections/{index}"] = ("section", index)

    return lookup


def _collect_child_sections(sections: List[DocumentSection]) -> set[int]:
    child_indices: set[int] = set()
    for section in sections:
        if not section.elements:
            continue
        for element_id in section.elements:
            if element_id.startswith("#/sections/"):
                try:
                    child_indices.add(int(element_id.rsplit("/", maxsplit=1)[-1]))
                except ValueError:
                    continue
    return child_indices


def main() -> int:
    args = parse_args()
    client = build_client()
    try:
        result = analyze_document(client, args.document)
    except FileNotFoundError:
        print(f"Could not find document: {args.document}", file=sys.stderr)
        return 1

    print_paragraphs(result)
    print_tables(result)
    print_sections(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
