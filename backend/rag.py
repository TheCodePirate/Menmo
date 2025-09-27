"""Simple Retrieval-Augmented Generation utilities for Menmo."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from .azure_integration import get_azure_integration
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
    data_path = Path(__file__).parent / "data" / "documents.json"
    if not data_path.exists():
        return []
    data = json.loads(data_path.read_text())
    documents = []
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
        # Lazily resolve Azure clients; this keeps tests fast and enables
        # optional Azure-powered retrieval when credentials are provided.
        self._azure = get_azure_integration()

    def search(
        self,
        query: str,
        grant_reference: Optional[Grant] = None,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        if not query:
            return []

        # Attempt Azure Cognitive Search first when configured.
        if self._azure.is_search_enabled:
            grant_slug = None
            if grant_reference is not None and grant_reference.title:
                grant_slug = self._to_slug(grant_reference.title)
            azure_results = self._azure.retrieve(
                query=query,
                grant_slug=grant_slug,
                top_k=top_k,
            )
            if azure_results:
                return azure_results

        if not self._documents:
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
