"""Simple Retrieval-Augmented Generation utilities for Menmo."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from .matching import SimpleTfidfEncoder, _cosine_similarity
from .models import Grant


@dataclass
class DocumentChunk:
    """Represents a retrievable knowledge paragraph."""

    id: str
    title: str
    content: str
    citation: Dict[str, Any]
    grant_slugs: Sequence[str]
    proprietary: bool = False


def _load_documents() -> List[DocumentChunk]:
    data_dir = Path(__file__).parent / "data"
    documents: List[DocumentChunk] = []
    for filename in ("documents.json", "scraped_documents.json"):
        data_path = data_dir / filename
        if not data_path.exists():
            continue
        data = json.loads(data_path.read_text())
        for item in data.get("documents", []):
            documents.append(
                DocumentChunk(
                    id=item.get("id", "doc"),
                    title=item.get("title", "Document"),
                    content=item.get("content", ""),
                    citation=item.get("citation", {}),
                    grant_slugs=item.get("grant_slugs", []),
                    proprietary=bool(item.get("proprietary", False)),
                )
            )
    return documents


class RAGEngine:
    """Small-footprint retrieval engine for contextual grounding."""

    def __init__(self, documents: Optional[Sequence[DocumentChunk]] = None) -> None:
        self._documents: List[DocumentChunk] = list(documents or _load_documents())
        self._encoder = SimpleTfidfEncoder()
        self._matrix: Optional[np.ndarray] = None
        if self._documents:
            self._matrix = self._encoder.fit_transform([doc.content for doc in self._documents])

    def search(
        self,
        query: str,
        grant_reference: Optional[Grant] = None,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        if not query or not self._documents:
            return []
        indices = list(range(len(self._documents)))
        if grant_reference is not None and grant_reference.url:
            slug = self._to_slug(grant_reference.title)
            indices = [
                idx
                for idx, doc in enumerate(self._documents)
                if not doc.grant_slugs or slug in doc.grant_slugs
            ]
        if not indices:
            return []
        matrix = self._matrix[indices] if self._matrix is not None else None
        if matrix is None:
            return []
        query_vec = self._encoder.transform([query])
        scores = _cosine_similarity(matrix, query_vec)
        paired = [
            (self._documents[idx], float(score))
            for idx, score in zip(indices, scores)
        ]
        paired.sort(key=lambda item: item[1], reverse=True)
        results = []
        for document, score in paired[:top_k]:
            results.append(
                {
                    "id": document.id,
                    "title": document.title,
                    "content": document.content,
                    "citation": document.citation,
                    "proprietary": document.proprietary,
                    "score": score,
                }
            )
        return results

    def _to_slug(self, value: str) -> str:
        return "".join(ch.lower() for ch in value if ch.isalnum())
