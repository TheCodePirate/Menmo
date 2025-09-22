"""Matching logic that ranks grants for a user profile."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Sequence

import numpy as np
from sqlalchemy.orm import Session

from .models import Grant, Match, UserProfile

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - fallback to lightweight encoder
    SentenceTransformer = None  # type: ignore


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between matrix *a* and vector *b*."""

    if a.size == 0 or b.size == 0:
        return np.zeros(a.shape[0])
    a_norm = np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = np.linalg.norm(b, axis=1, keepdims=True)
    a_norm[a_norm == 0] = 1
    b_norm[b_norm == 0] = 1
    return (a @ b.T).flatten() / (a_norm.flatten() * b_norm.flatten()[0])


class SimpleTfidfEncoder:
    """A lightweight TF-IDF encoder used when transformers are unavailable."""

    TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")

    def __init__(self) -> None:
        self.vocabulary_: dict[str, int] | None = None
        self.idf_: dict[str, float] | None = None

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in self.TOKEN_PATTERN.findall(text)]

    def _fit(self, tokenized_docs: Sequence[List[str]]) -> None:
        doc_freq: Counter[str] = Counter()
        for tokens in tokenized_docs:
            doc_freq.update(set(tokens))

        vocab = {token: idx for idx, token in enumerate(sorted(doc_freq))}
        num_docs = len(tokenized_docs)
        idf = {token: math.log((1 + num_docs) / (1 + freq)) + 1 for token, freq in doc_freq.items()}

        self.vocabulary_ = vocab
        self.idf_ = idf

    def fit_transform(self, docs: Sequence[str]) -> np.ndarray:
        tokenized = [self._tokenize(doc) for doc in docs]
        self._fit(tokenized)
        return self._transform(tokenized)

    def transform(self, docs: Sequence[str]) -> np.ndarray:
        if self.vocabulary_ is None or self.idf_ is None:
            raise RuntimeError("Vectorizer has not been fitted")
        tokenized = [self._tokenize(doc) for doc in docs]
        return self._transform(tokenized)

    def _transform(self, tokenized_docs: Sequence[List[str]]) -> np.ndarray:
        vocab = self.vocabulary_ or {}
        idf = self.idf_ or {}
        matrix = np.zeros((len(tokenized_docs), len(vocab)), dtype=float)
        for row, tokens in enumerate(tokenized_docs):
            if not tokens:
                continue
            counts = Counter(tokens)
            length = float(sum(counts.values()))
            for token, count in counts.items():
                idx = vocab.get(token)
                if idx is None:
                    continue
                matrix[row, idx] = (count / length) * idf.get(token, 0.0)
        return matrix


@dataclass
class RankedMatch:
    """Represents a ranked match result."""

    grant: Grant
    score: float


class MatchingService:
    """Service encapsulating the matching algorithm."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or "all-MiniLM-L6-v2"
        self._transformer = None
        if SentenceTransformer is not None:
            try:
                self._transformer = SentenceTransformer(self._model_name)
            except Exception:
                # Downloading models may fail in restricted environments; fallback to TF-IDF.
                self._transformer = None

    def _encode(self, documents: Sequence[str]) -> np.ndarray:
        """Encode documents into dense vectors."""

        if not documents:
            return np.empty((0, 0))

        if self._transformer is not None:
            embeddings = self._transformer.encode(list(documents))
            return np.asarray(embeddings, dtype=float)

        vectorizer = SimpleTfidfEncoder()
        return vectorizer.fit_transform(documents)

    def _build_user_document(self, user: UserProfile) -> str:
        parts = [user.name, user.organization or "", user.focus_areas or "", user.goals or ""]
        return "\n".join(part for part in parts if part)

    def _build_grant_document(self, grant: Grant) -> str:
        parts = [grant.title, grant.description, grant.sponsor or "", grant.deadline or ""]
        return "\n".join(part for part in parts if part)

    def generate_matches(
        self,
        session: Session,
        user: UserProfile,
        grants: Iterable[Grant] | None = None,
        top_k: int = 5,
    ) -> List[RankedMatch]:
        """Return ranked matches for a user."""

        grants_list = list(grants if grants is not None else session.query(Grant).all())
        if not grants_list:
            return []

        user_document = self._build_user_document(user)
        grant_documents = [self._build_grant_document(grant) for grant in grants_list]

        documents = grant_documents + [user_document]
        embeddings = self._encode(documents)
        if embeddings.size == 0:
            return []

        grant_vectors = embeddings[:-1]
        user_vector = embeddings[-1].reshape(1, -1)
        similarities = _cosine_similarity(grant_vectors, user_vector)

        ranked: List[RankedMatch] = []
        for grant, score in zip(grants_list, similarities):
            ranked.append(RankedMatch(grant=grant, score=float(score)))

        ranked.sort(key=lambda item: item.score, reverse=True)
        top_matches = ranked[:top_k]

        # Persist matches for traceability.
        for item in top_matches:
            match = Match(user_id=user.id, grant_id=item.grant.id, score=item.score)
            session.merge(match)
        session.commit()

        return top_matches


def generate_matches(session: Session, user_id: int, top_k: int = 5) -> List[RankedMatch]:
    """Convenience wrapper to generate matches for a user id."""

    user = session.query(UserProfile).filter(UserProfile.id == user_id).one()
    service = MatchingService()
    return service.generate_matches(session=session, user=user, top_k=top_k)
