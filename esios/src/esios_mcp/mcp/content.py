"""Specialized LLM-facing tools for e·sios content."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios_mcp.api import CONTENT_TYPES, ESIOS_API_BASE_URL, ContentApi, EsiosApiClient

from .common import (
    run_api_call,
    validate_locale,
    validate_nonempty,
    validate_positive_id,
)


ContentType = Literal["maps", "documentations", "glossaries", "news", "static_pages", "umms"]
ContentOrder = Literal["published", "updated", "expires", "created"]


def _validate_type(resource_type: str) -> str:
    if resource_type not in CONTENT_TYPES:
        raise ValueError(f"resource_type must be one of: {', '.join(sorted(CONTENT_TYPES))}")
    return resource_type


def _list_request(
    *,
    resource_type: str,
    locale: str,
    taxonomy_terms: list[str] | None,
    vocabularies: list[str] | None,
    taxonomy_ids: list[int] | None,
    vocabulary_ids: list[int] | None,
    order: str | None,
    sticky: bool | None,
) -> dict:
    request = {
        "resource_type": resource_type,
        "locale": locale,
        "taxonomy_terms": taxonomy_terms,
        "vocabularies": vocabularies,
        "taxonomy_ids": taxonomy_ids,
        "vocabulary_ids": vocabulary_ids,
        "order": order,
        "sticky": sticky,
    }
    return {key: value for key, value in request.items() if value is not None}


async def esios_list_content(
    resource_type: ContentType,
    locale: Literal["es", "en"] = "es",
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    taxonomy_ids: list[int] | None = None,
    vocabulary_ids: list[int] | None = None,
    order: ContentOrder | None = None,
    sticky: bool | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """List maps, documentations, glossaries, news, static pages, or UMMs."""
    resource_type = _validate_type(resource_type)
    locale = validate_locale(locale)
    request = _list_request(
        resource_type=resource_type,
        locale=locale,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
        taxonomy_ids=taxonomy_ids,
        vocabulary_ids=vocabulary_ids,
        order=order,
        sticky=sticky,
    )
    return await run_api_call(
        ctx=ctx,
        operation=f"Content API list {resource_type}",
        url=f"{ESIOS_API_BASE_URL}/{locale}/{resource_type}",
        request=request,
        call=lambda: ContentApi(EsiosApiClient()).list(**request),
    )


async def esios_filter_news(
    locale: Literal["es", "en"] = "es",
    order: ContentOrder | None = None,
    sticky: bool | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    taxonomy_ids: list[int] | None = None,
    vocabulary_ids: list[int] | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Filter news by sticky state, ordering, taxonomy terms, or vocabulary."""
    locale = validate_locale(locale)
    request = _list_request(
        resource_type="news",
        locale=locale,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
        taxonomy_ids=taxonomy_ids,
        vocabulary_ids=vocabulary_ids,
        order=order,
        sticky=sticky,
    )
    return await run_api_call(
        ctx=ctx,
        operation="Content filter API news",
        url=f"{ESIOS_API_BASE_URL}/{locale}/news",
        request=request,
        call=lambda: ContentApi(EsiosApiClient()).list(**request),
    )


async def esios_get_content(
    resource_type: ContentType,
    identifier: int | str,
    locale: Literal["es", "en"] = "es",
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve one locale-prefixed content resource by slug or identifier."""
    resource_type = _validate_type(resource_type)
    locale = validate_locale(locale)
    if isinstance(identifier, int):
        identifier = validate_positive_id(identifier, "identifier")
    else:
        identifier = validate_nonempty(identifier, "identifier")
    request = {"resource_type": resource_type, "identifier": identifier, "locale": locale}
    return await run_api_call(
        ctx=ctx,
        operation=f"Content API get {resource_type}",
        url=f"{ESIOS_API_BASE_URL}/{locale}/{resource_type}/{identifier}",
        request=request,
        call=lambda: ContentApi(EsiosApiClient()).get(resource_type, identifier, locale=locale),
    )


async def esios_get_content_by_id(
    content_id: int,
    locale: Literal["es", "en"] = "es",
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve content through the shared `/contents/{id}` route."""
    content_id = validate_positive_id(content_id, "content_id")
    locale = validate_locale(locale)
    request = {"content_id": content_id, "locale": locale}
    return await run_api_call(
        ctx=ctx,
        operation="Content API get by ID",
        url=f"{ESIOS_API_BASE_URL}/contents/{content_id}",
        request=request,
        call=lambda: ContentApi(EsiosApiClient()).get_by_id(content_id, locale=locale),
    )
