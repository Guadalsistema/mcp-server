"""Representations of e·sios Content and content-filter endpoints."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .client import EsiosApiClient


CONTENT_TYPES = frozenset(
    {"maps", "documentations", "glossaries", "news", "static_pages", "umms"}
)


def _content_params(
    *,
    locale: str,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    taxonomy_ids: list[int] | None = None,
    vocabulary_ids: list[int] | None = None,
    order: str | None = None,
    sticky: bool | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"locale": locale}
    if taxonomy_terms:
        params["taxonomy_terms[]"] = taxonomy_terms
    if vocabularies:
        params["vocabularies[]"] = vocabularies
    if taxonomy_ids:
        params["taxonomy_ids[]"] = [str(value) for value in taxonomy_ids]
    if vocabulary_ids:
        params["vocabulary_ids[]"] = [str(value) for value in vocabulary_ids]
    if order is not None:
        params["order"] = order
    if sticky is not None:
        params["sticky"] = "true" if sticky else "false"
    return params


class ContentApi:
    """Endpoint methods for the six locale-prefixed content resources."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def list(
        self,
        resource_type: str,
        *,
        locale: str = "es",
        taxonomy_terms: list[str] | None = None,
        vocabularies: list[str] | None = None,
        taxonomy_ids: list[int] | None = None,
        vocabulary_ids: list[int] | None = None,
        order: str | None = None,
        sticky: bool | None = None,
    ) -> dict[str, Any]:
        return self.client.get(
            f"/{locale}/{resource_type}",
            params=_content_params(
                locale=locale,
                taxonomy_terms=taxonomy_terms,
                vocabularies=vocabularies,
                taxonomy_ids=taxonomy_ids,
                vocabulary_ids=vocabulary_ids,
                order=order,
                sticky=sticky,
            ),
        )

    def get(
        self,
        resource_type: str,
        identifier: int | str,
        *,
        locale: str = "es",
    ) -> dict[str, Any]:
        return self.client.get(
            f"/{locale}/{resource_type}/{quote(str(identifier), safe='')}",
            params={"locale": locale},
        )

    def get_by_id(self, content_id: int, *, locale: str = "es") -> dict[str, Any]:
        return self.client.get("/contents/" + str(content_id), params={"locale": locale})
