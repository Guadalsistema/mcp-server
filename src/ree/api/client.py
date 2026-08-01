"""HTTP client and resource helpers for the REE APIs."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import requests


REE_API_BASE_URL = "https://apidatos.ree.es"
REE_GLOSSARY_URLS = {
    "es": "https://www.ree.es/es/glosario",
    "en": "https://www.ree.es/en/glossary",
}

VALID_LANGUAGES = frozenset(REE_GLOSSARY_URLS)
VALID_CATEGORIES = frozenset(
    {"balance", "demanda", "generacion", "intercambios", "mercados", "transporte"}
)
VALID_TIME_TRUNCS = frozenset({"hour", "day", "month", "year"})
VALID_GEO_TRUNCS = frozenset({"electric_system"})
VALID_GEO_LIMITS = frozenset(
    {"peninsular", "canarias", "baleares", "ceuta", "melilla", "ccaa"}
)
# This legacy real-time widget returns the national curve only. Regional
# real-time curves are served by REE's separate Visiona service.
NATIONAL_ONLY_WIDGETS = frozenset({"demanda-tiempo-real"})
SLUG_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")


class ReeApiError(RuntimeError):
    """Raised when REE cannot return a usable response."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.retryable = retryable


def _validate_choice(value: str, field_name: str, choices: set[str] | frozenset[str]) -> str:
    if value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"{field_name} must be one of: {allowed}")
    return value


def _validate_slug(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not SLUG_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} must be a URL slug")
    return value


def _normalize_datetime(value: str, field_name: str) -> tuple[str, datetime]:
    if not isinstance(value, str) or "T" not in value:
        raise ValueError(f"{field_name} must use YYYY-MM-DDTHH:MM format")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must use YYYY-MM-DDTHH:MM format") from error
    return parsed.strftime("%Y-%m-%dT%H:%M"), parsed.replace(tzinfo=None)


def build_data_request(
    lang: str,
    category: str,
    widget: str,
    start_date: str,
    end_date: str,
    time_trunc: str,
    geo_trunc: str | None = None,
    geo_limit: str | None = None,
    geo_ids: str | None = None,
) -> tuple[str, dict[str, str]]:
    """Validate tool arguments and build the official REData request."""
    _validate_choice(lang, "lang", VALID_LANGUAGES)
    _validate_choice(category, "category", VALID_CATEGORIES)
    _validate_slug(widget, "widget")
    _validate_choice(time_trunc, "time_trunc", VALID_TIME_TRUNCS)

    normalized_start, parsed_start = _normalize_datetime(start_date, "start_date")
    normalized_end, parsed_end = _normalize_datetime(end_date, "end_date")
    if parsed_start > parsed_end:
        raise ValueError("start_date must be on or before end_date")

    if geo_trunc is not None:
        _validate_choice(geo_trunc, "geo_trunc", VALID_GEO_TRUNCS)
    if geo_limit is not None:
        _validate_choice(geo_limit, "geo_limit", VALID_GEO_LIMITS)
    if geo_ids is not None and (
        not isinstance(geo_ids, str) or not re.fullmatch(r"\d+", geo_ids)
    ):
        raise ValueError("geo_ids must be a numeric string")

    geography = (geo_trunc, geo_limit, geo_ids)
    if any(value is not None for value in geography) and not all(
        value is not None for value in geography
    ):
        raise ValueError("geo_trunc, geo_limit, and geo_ids must be supplied together")
    if widget in NATIONAL_ONLY_WIDGETS and any(value is not None for value in geography):
        raise ValueError(
            f"widget {widget} only provides the national real-time curve and "
            "does not support geographic filters"
        )

    params = {
        "start_date": normalized_start,
        "end_date": normalized_end,
        "time_trunc": time_trunc,
    }
    if geo_trunc is not None:
        params["geo_trunc"] = geo_trunc
        params["geo_limit"] = str(geo_limit)
        params["geo_ids"] = str(geo_ids)
    return f"{REE_API_BASE_URL}/{lang}/datos/{category}/{widget}", params


def _response_error(response: requests.Response) -> str:
    """Extract REE's JSON:API error details without assuming JSON content."""
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict) and payload.get("errors"):
        messages = []
        for item in payload["errors"]:
            if isinstance(item, dict):
                detail = item.get("detail") or item.get("title")
                if detail:
                    messages.append(str(detail))
        if messages:
            return "; ".join(messages)
    text = response.text.strip()
    if text and not re.search(r"<\s*!?doctype|<\s*html\b|<\s*body\b", text, re.I):
        return text[:500]
    return f"HTTP {response.status_code}"


def fetch_json(url: str, params: dict[str, str], timeout: int = 60) -> dict[str, Any]:
    """Fetch and validate one REE JSON response."""
    try:
        response = requests.get(
            url,
            params=params,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
    except requests.RequestException as error:
        raise ReeApiError(
            "REE could not be reached. Retry the request later.",
            code="ree_network_error",
            retryable=True,
        ) from error

    if response.status_code >= 400:
        retryable = response.status_code == 429 or response.status_code >= 500
        if retryable:
            message = (
                f"REE is temporarily unavailable (HTTP {response.status_code}). "
                "Retry the request later."
            )
        else:
            message = (
                f"REE rejected the request (HTTP {response.status_code}): "
                f"{_response_error(response)}"
            )
        raise ReeApiError(
            message,
            code="ree_upstream_unavailable" if retryable else "ree_request_rejected",
            status_code=response.status_code,
            retryable=retryable,
        )

    try:
        payload = response.json()
    except ValueError as error:
        raise ReeApiError(
            "REE returned an invalid response. Retry the request later.",
            code="ree_invalid_response",
            status_code=response.status_code,
            retryable=True,
        ) from error

    if not isinstance(payload, dict):
        raise ReeApiError(
            "REE returned an unexpected response format.",
            code="ree_invalid_response",
            status_code=response.status_code,
            retryable=True,
        )
    if payload.get("errors"):
        raise ReeApiError(
            f"REE rejected the request: {_response_error(response)}",
            code="ree_api_error",
            status_code=response.status_code,
        )
    return payload

