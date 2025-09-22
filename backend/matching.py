"""Simple AI-inspired matching logic for grants and user profiles."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List

from sqlalchemy.orm import Session

from backend.models import Grant, User

_TOKEN_PATTERN = re.compile(r"\b\w+\b")


@dataclass
class MatchResult:
    """Represents a grant match with an associated score."""

    grant: Grant
    score: float


def _tokenize(text: str) -> Iterable[str]:
    return _TOKEN_PATTERN.findall(text.lower())


def embed_text(text: str) -> Counter[str]:
    """Create a sparse bag-of-words embedding for the supplied text."""
    return Counter(_tokenize(text))


def cosine_similarity(vec_a: Counter[str], vec_b: Counter[str]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    dot_product = sum(value * vec_b.get(token, 0) for token, value in vec_a.items())
    norm_a = math.sqrt(sum(value * value for value in vec_a.values()))
    norm_b = math.sqrt(sum(value * value for value in vec_b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return dot_product / (norm_a * norm_b)


def _user_embedding(user: User) -> Counter[str]:
    text = " ".join(
        filter(
            None,
            [user.name, user.organization, user.interests, user.goals],
        )
    )
    return embed_text(text)


def _grant_embedding(grant: Grant) -> Counter[str]:
    text = " ".join(
        filter(
            None,
            [grant.title, grant.description, grant.focus_area, grant.sponsor],
        )
    )
    return embed_text(text)


def rank_grants_for_user(
    session: Session,
    user_id: int,
    *,
    top_k: int = 5,
    min_score: float = 0.0,
) -> List[MatchResult]:
    """Rank available grants for a user using cosine similarity."""
    user = session.get(User, user_id)
    if user is None:
        raise ValueError(f"User with id={user_id} was not found.")

    user_vector = _user_embedding(user)

    matches: List[MatchResult] = []
    for grant in session.query(Grant).all():
        grant_vector = _grant_embedding(grant)
        score = cosine_similarity(user_vector, grant_vector)
        if score >= min_score:
            matches.append(MatchResult(grant=grant, score=score))

    matches.sort(key=lambda match: match.score, reverse=True)
    return matches[:top_k]
