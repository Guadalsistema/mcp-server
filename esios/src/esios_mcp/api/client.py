"""HTTP client and error handling for the e·sios API."""

from __future__ import annotations

import os
import re
from typing import Any, Mapping
from urllib.parse import urljoin

import requests


ESIOS_API_BASE_URL = "https://api.esios.ree.es"


class EsiosApiError(RuntimeError):
    """Raised when e·sios cannot return a usable response."""

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


def _response_error(response: requests.Response) -> str:
    """Extract a useful API error without returning an HTML error page."""
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        errors = payload.get("errors")
        if isinstance(errors, list):
            messages = []
            for item in errors:
                if isinstance(item, dict):
                    detail = item.get("detail") or item.get("title") or item.get("message")
                    if detail:
                        messages.append(str(detail))
                elif item:
                    messages.append(str(item))
            if messages:
                return "; ".join(messages)

        for key in ("error", "message", "detail"):
            if payload.get(key):
                return str(payload[key])

    text = response.text.strip()
    if text and not re.search(r"<\s*!?doctype|<\s*html\b|<\s*body\b", text, re.I):
        return text[:500]
    return f"HTTP {response.status_code}"


class EsiosApiClient:
    """Small authenticated client for JSON e·sios endpoints."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = ESIOS_API_BASE_URL,
        timeout: int = 60,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("ESIOS_API_KEY")
        if not self.api_key:
            raise EsiosApiError(
                "ESIOS_API_KEY is required to call the e·sios API.",
                code="esios_missing_api_key",
            )
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = session or requests.Session()

    def url_for(self, path: str) -> str:
        """Return an absolute URL for an API path."""
        return urljoin(self.base_url, path.lstrip("/"))

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        api_version: str = "v1",
    ) -> dict[str, Any]:
        """Perform an authenticated GET and return the upstream JSON object."""
        url = self.url_for(path)
        headers = {
            "Accept": f"application/json; application/vnd.esios-api-{api_version}+json",
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }

        try:
            response = self.session.get(
                url,
                params=dict(params or {}),
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as error:
            raise EsiosApiError(
                "e·sios could not be reached. Retry the request later.",
                code="esios_network_error",
                retryable=True,
            ) from error

        if response.status_code >= 400:
            retryable = response.status_code == 429 or response.status_code >= 500
            if retryable:
                message = (
                    f"e·sios is temporarily unavailable (HTTP {response.status_code}). "
                    "Retry the request later."
                )
            else:
                message = (
                    f"e·sios rejected the request (HTTP {response.status_code}): "
                    f"{_response_error(response)}"
                )
            raise EsiosApiError(
                message,
                code="esios_upstream_unavailable" if retryable else "esios_request_rejected",
                status_code=response.status_code,
                retryable=retryable,
            )

        try:
            payload = response.json()
        except ValueError as error:
            raise EsiosApiError(
                "e·sios returned an invalid JSON response. Retry the request later.",
                code="esios_invalid_response",
                status_code=response.status_code,
                retryable=True,
            ) from error

        if not isinstance(payload, dict):
            raise EsiosApiError(
                "e·sios returned an unexpected response format.",
                code="esios_invalid_response",
                status_code=response.status_code,
                retryable=True,
            )
        return payload
