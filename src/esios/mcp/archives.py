"""Specialized LLM-facing tools for e·sios archives."""

from __future__ import annotations

from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult

from esios.api import ESIOS_API_BASE_URL, ArchivesApi, EsiosApiClient

from .common import (
    run_api_call,
    run_download,
    validate_date_range,
    validate_locale,
    validate_positive_id,
)


DateType = Literal["datos", "publicacion"]


def _request(
    *,
    locale: str,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    date_type: str | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
) -> dict:
    request = {
        "locale": locale,
        "date": date,
        "start_date": start_date,
        "end_date": end_date,
        "date_type": date_type,
        "taxonomy_terms": taxonomy_terms,
        "vocabularies": vocabularies,
    }
    return {key: value for key, value in request.items() if value is not None}


def _validate_dates(start_date: str | None, end_date: str | None) -> None:
    validate_date_range(start_date, end_date)


async def esios_list_archives(
    locale: Literal["es", "en"] = "es",
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    date_type: DateType | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """List PDF archives with optional dates, date type, and taxonomy filters."""
    locale = validate_locale(locale)
    _validate_dates(start_date, end_date)
    request = _request(
        locale=locale,
        date=date,
        start_date=start_date,
        end_date=end_date,
        date_type=date_type,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
    )
    return await run_api_call(
        ctx=ctx,
        operation="Archive API list",
        url=f"{ESIOS_API_BASE_URL}/archives",
        request=request,
        call=lambda: ArchivesApi(EsiosApiClient()).list(**request),
    )


async def esios_get_archive(
    archive_id: int,
    locale: Literal["es", "en"] = "es",
    date: str | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve one archive metadata record by ID."""
    archive_id = validate_positive_id(archive_id, "archive_id")
    locale = validate_locale(locale)
    request = _request(
        locale=locale,
        date=date,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
    )
    request["archive_id"] = archive_id
    return await run_api_call(
        ctx=ctx,
        operation="Archive API get",
        url=f"{ESIOS_API_BASE_URL}/archives/{archive_id}",
        request=request,
        call=lambda: ArchivesApi(EsiosApiClient()).get(archive_id, **{k: v for k, v in request.items() if k != "archive_id"}),
    )


async def esios_get_archive_calculator_data(
    archive_id: int,
    start_date: str,
    end_date: str,
    locale: Literal["es", "en"] = "es",
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve JSON calculation data for an archive and date range."""
    archive_id = validate_positive_id(archive_id, "archive_id")
    locale = validate_locale(locale)
    _validate_dates(start_date, end_date)
    request = _request(
        locale=locale,
        start_date=start_date,
        end_date=end_date,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
    )
    request["archive_id"] = archive_id
    return await run_api_call(
        ctx=ctx,
        operation="Archive calculator API",
        url=f"{ESIOS_API_BASE_URL}/calculator-data/{archive_id}",
        request=request,
        call=lambda: ArchivesApi(EsiosApiClient()).calculator_data(
            archive_id,
            **{k: v for k, v in request.items() if k != "archive_id"},
        ),
    )


async def esios_download_archive(
    archive_id: int,
    locale: Literal["es", "en"] = "es",
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    date_type: DateType | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Download an archive as base64 with content type and size metadata."""
    archive_id = validate_positive_id(archive_id, "archive_id")
    locale = validate_locale(locale)
    _validate_dates(start_date, end_date)
    request = _request(
        locale=locale,
        date=date,
        start_date=start_date,
        end_date=end_date,
        date_type=date_type,
    )
    request["archive_id"] = archive_id
    return await run_download(
        ctx=ctx,
        operation="Archive download API",
        url=f"{ESIOS_API_BASE_URL}/archives/{archive_id}/download",
        request=request,
        call=lambda: ArchivesApi(EsiosApiClient()).download(
            archive_id,
            **{k: v for k, v in request.items() if k != "archive_id"},
        ),
    )


async def esios_list_json_archives(
    locale: Literal["es", "en"] = "es",
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """List archives whose downloadable values are JSON."""
    locale = validate_locale(locale)
    _validate_dates(start_date, end_date)
    request = _request(
        locale=locale,
        date=date,
        start_date=start_date,
        end_date=end_date,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
    )
    return await run_api_call(
        ctx=ctx,
        operation="Archive JSON API list",
        url=f"{ESIOS_API_BASE_URL}/archives_json",
        request=request,
        call=lambda: ArchivesApi(EsiosApiClient()).list_json(**request),
    )


async def esios_get_json_archive(
    archive_id: int,
    locale: Literal["es", "en"] = "es",
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Retrieve metadata for one JSON archive by ID."""
    archive_id = validate_positive_id(archive_id, "archive_id")
    locale = validate_locale(locale)
    _validate_dates(start_date, end_date)
    request = _request(
        locale=locale,
        date=date,
        start_date=start_date,
        end_date=end_date,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
    )
    request["archive_id"] = archive_id
    return await run_api_call(
        ctx=ctx,
        operation="Archive JSON API get",
        url=f"{ESIOS_API_BASE_URL}/archives/{archive_id}",
        request=request,
        call=lambda: ArchivesApi(EsiosApiClient()).get_json_archive(
            archive_id,
            **{k: v for k, v in request.items() if k != "archive_id"},
        ),
    )


async def esios_download_json_archive(
    archive_id: int,
    locale: Literal["es", "en"] = "es",
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
    ctx: Context | None = None,
) -> str | ToolResult:
    """Download and preserve the JSON value of one JSON archive."""
    archive_id = validate_positive_id(archive_id, "archive_id")
    locale = validate_locale(locale)
    _validate_dates(start_date, end_date)
    request = _request(
        locale=locale,
        date=date,
        start_date=start_date,
        end_date=end_date,
        taxonomy_terms=taxonomy_terms,
        vocabularies=vocabularies,
    )
    request["archive_id"] = archive_id
    return await run_api_call(
        ctx=ctx,
        operation="Archive JSON download API",
        url=f"{ESIOS_API_BASE_URL}/archives/{archive_id}/download_json",
        request=request,
        call=lambda: ArchivesApi(EsiosApiClient()).download_json(
            archive_id,
            **{k: v for k, v in request.items() if k != "archive_id"},
        ),
    )
