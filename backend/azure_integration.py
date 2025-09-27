"""Optional Azure Search + OpenAI integration helpers.

This module adapts utility functions from the Azure Search + OpenAI demo
project (MIT licensed) so that Menmo can leverage the same patterns when
Azure credentials are available. All helpers are written to degrade
gracefully when Azure dependencies or configuration are missing to keep the
existing offline test suite functioning.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import httpx

try:  # Optional dependency – only required when Azure OpenAI is used.
    from openai import AzureOpenAI
except Exception:  # pragma: no cover - keep optional during tests
    AzureOpenAI = None  # type: ignore


logger = logging.getLogger(__name__)


def clean_key_if_exists(key: Optional[str]) -> Optional[str]:
    """Normalize environment keys.

    Copied from Azure's ``prepdocs.clean_key_if_exists`` helper so we reuse the
    same sanitisation semantics the demo relies on when loading credentials.
    """

    if key is not None and key.strip() != "":
        return key.strip()
    return None


def _normalize_endpoint(endpoint: Optional[str], service: Optional[str]) -> Optional[str]:
    """Resolve the Azure Cognitive Search endpoint from configuration."""

    endpoint = clean_key_if_exists(endpoint)
    service = clean_key_if_exists(service)
    if endpoint:
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint.lstrip('https://')}"
        return endpoint.rstrip("/")
    if service:
        return f"https://{service}.search.windows.net"
    return None


@dataclass
class AzureSearchConfig:
    endpoint: str
    index: str
    api_key: str

    @property
    def search_url(self) -> str:
        return f"{self.endpoint}/indexes/{self.index}/docs/search?api-version=2023-11-01"

    @classmethod
    def from_env(cls) -> Optional["AzureSearchConfig"]:
        endpoint = _normalize_endpoint(
            os.getenv("AZURE_SEARCH_ENDPOINT"), os.getenv("AZURE_SEARCH_SERVICE")
        )
        index = clean_key_if_exists(os.getenv("AZURE_SEARCH_INDEX"))
        api_key = clean_key_if_exists(
            os.getenv("AZURE_SEARCH_KEY") or os.getenv("AZURE_SEARCH_API_KEY")
        )
        if endpoint and index and api_key:
            return cls(endpoint=endpoint, index=index, api_key=api_key)
        return None


class AzureSearchClient:
    """Minimal REST client for Azure Cognitive Search."""

    def __init__(self, config: AzureSearchConfig):
        self._config = config

    def search(
        self,
        *,
        query: str,
        top: int = 3,
        filter_expression: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "search": query or "*",
            "top": top,
        }
        if filter_expression:
            payload["filter"] = filter_expression

        headers = {
            "api-key": self._config.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(self._config.search_url, json=payload, headers=headers, timeout=8.0)
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - network failures are optional
            logger.debug("Azure search request failed: %s", exc)
            return []

        data = response.json()
        return list(data.get("value", []))


@dataclass
class AzureOpenAIConfig:
    endpoint: str
    api_key: str
    deployment: str
    api_version: str = "2024-06-01"
    temperature: float = 0.2
    max_tokens: int = 400

    @classmethod
    def from_env(cls) -> Optional["AzureOpenAIConfig"]:
        endpoint = clean_key_if_exists(os.getenv("AZURE_OPENAI_ENDPOINT"))
        api_key = clean_key_if_exists(os.getenv("AZURE_OPENAI_API_KEY"))
        deployment = clean_key_if_exists(
            os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
            or os.getenv("AZURE_OPENAI_DEPLOYMENT")
            or os.getenv("AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT")
        )
        api_version = clean_key_if_exists(os.getenv("AZURE_OPENAI_API_VERSION"))
        temperature = os.getenv("AZURE_OPENAI_TEMPERATURE")
        max_tokens = os.getenv("AZURE_OPENAI_MAX_TOKENS")
        if endpoint and api_key and deployment:
            return cls(
                endpoint=endpoint.rstrip("/"),
                api_key=api_key,
                deployment=deployment,
                api_version=api_version or cls.api_version,
                temperature=float(temperature) if temperature is not None else cls.temperature,
                max_tokens=int(max_tokens) if max_tokens is not None else cls.max_tokens,
            )
        return None


class AzureOpenAIClient:
    """Thin wrapper around the Azure OpenAI chat completions API."""

    def __init__(self, config: AzureOpenAIConfig):
        if AzureOpenAI is None:  # pragma: no cover - optional dependency
            raise RuntimeError("Azure OpenAI SDK is not installed")
        self._deployment = config.deployment
        self._temperature = config.temperature
        self._max_tokens = config.max_tokens
        self._client = AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.endpoint,
        )

    def complete_chat(self, *, system_prompt: str, user_prompt: str) -> Optional[str]:
        try:
            response = self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
        except Exception as exc:  # pragma: no cover - depends on external service
            logger.debug("Azure OpenAI request failed: %s", exc)
            return None

        if not response.choices:
            return None
        return response.choices[0].message.content or None


class AzureIntegration:
    """Coordinates Azure Search retrieval and Azure OpenAI generation."""

    def __init__(self) -> None:
        self._search_config = AzureSearchConfig.from_env()
        self._openai_config = AzureOpenAIConfig.from_env()
        self._search_client = (
            AzureSearchClient(self._search_config) if self._search_config is not None else None
        )
        self._openai_client: Optional[AzureOpenAIClient]
        if self._openai_config is not None:
            try:
                self._openai_client = AzureOpenAIClient(self._openai_config)
            except Exception as exc:  # pragma: no cover - optional dependency may not exist
                logger.debug("Failed to initialise Azure OpenAI client: %s", exc)
                self._openai_client = None
        else:
            self._openai_client = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def is_search_enabled(self) -> bool:
        return self._search_client is not None

    @property
    def is_generation_enabled(self) -> bool:
        return self._openai_client is not None

    # ------------------------------------------------------------------
    # Retrieval & Generation helpers
    # ------------------------------------------------------------------
    def retrieve(
        self,
        *,
        query: str,
        grant_slug: Optional[str] = None,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        if self._search_client is None:
            return []

        filter_expression = None
        if grant_slug:
            filter_expression = f"grantSlugs/any(s: s eq '{grant_slug}')"

        raw_results = self._search_client.search(
            query=query,
            top=top_k,
            filter_expression=filter_expression,
        )
        return [self._convert_search_result(item) for item in raw_results]

    def generate_application_section(
        self,
        *,
        section_key: str,
        section_title: str,
        grant_title: str,
        grant_description: str,
        project_summary: str,
        organization: str,
        blockers: Iterable[str],
        rag_chunks: Iterable[Dict[str, Any]],
    ) -> Optional[str]:
        if self._openai_client is None:
            return None

        knowledge_lines = []
        for chunk in rag_chunks:
            citation = chunk.get("citation", {})
            citation_parts = [citation.get("title"), citation.get("section"), citation.get("url")]
            citation_text = " | ".join(part for part in citation_parts if part)
            knowledge_lines.append(f"- {chunk.get('content', '')[:500]} ({citation_text})")

        blocker_text = "\n".join(f"- {item}" for item in blockers if item)
        knowledge_text = "\n".join(knowledge_lines)

        system_prompt = (
            "You are an assistant helping climate grant applicants craft persuasive "
            "and compliant application narratives."
        )
        user_prompt = (
            f"Write the '{section_title}' section for a grant application.\n"
            f"Grant: {grant_title}.\n"
            f"Grant summary: {grant_description}.\n"
            f"Applicant organisation: {organization}.\n"
            f"Project overview: {project_summary}.\n"
            f"Address any blockers: {blocker_text or 'None identified.'}\n"
            f"Relevant knowledge:\n{knowledge_text or 'No external knowledge available.'}\n"
            f"Focus on actionable, specific details and keep the tone factual."
        )

        return self._openai_client.complete_chat(
            system_prompt=system_prompt, user_prompt=user_prompt
        )

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _convert_search_result(self, item: Dict[str, Any]) -> Dict[str, Any]:
        citation = {
            "title": item.get("title") or item.get("sourcepage") or item.get("sourcefile"),
            "section": item.get("section"),
            "url": item.get("url") or item.get("sourcefile"),
            "source_type": item.get("sourceType"),
        }
        # Remove keys with None values for cleaner payloads.
        citation = {key: value for key, value in citation.items() if value}

        return {
            "id": item.get("id") or item.get("chunkId") or item.get("documentId") or "azure-doc",
            "title": item.get("title") or item.get("sourcepage") or "Azure Document",
            "content": item.get("content")
            or item.get("text")
            or item.get("chunk")
            or "",
            "citation": citation,
            "proprietary": bool(item.get("proprietary", False)),
            "score": float(item.get("@search.score", 0.0)),
            "grant_slugs": item.get("grantSlugs") or [],
        }


_AZURE_SINGLETON: Optional[AzureIntegration] = None


def get_azure_integration() -> AzureIntegration:
    """Return a lazily constructed Azure integration helper."""

    global _AZURE_SINGLETON
    if _AZURE_SINGLETON is None:
        _AZURE_SINGLETON = AzureIntegration()
    return _AZURE_SINGLETON

