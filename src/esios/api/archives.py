"""Representations of e·sios Archive and Archive JSON endpoints."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .client import EsiosApiClient


def _params(
    *,
    locale: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    date_type: str | None = None,
    taxonomy_terms: list[str] | None = None,
    vocabularies: list[str] | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "locale": locale,
        "date": date,
        "start_date": start_date,
        "end_date": end_date,
        "date_type": date_type,
    }
    params = {key: value for key, value in params.items() if value is not None}
    if taxonomy_terms:
        params["taxonomy_terms[]"] = taxonomy_terms
    if vocabularies:
        params["vocabularies[]"] = vocabularies
    return params


class ArchivesApi:
    """Endpoint methods for Archive, Archive JSON, calculator, and downloads."""

    def __init__(self, client: EsiosApiClient) -> None:
        self.client = client

    def list(
        self,
        *,
        locale: str = "es",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        date_type: str | None = None,
        taxonomy_terms: list[str] | None = None,
        vocabularies: list[str] | None = None,
    ) -> dict[str, Any]:
        return self.client.get(
            "/archives",
            params=_params(
                locale=locale,
                date=date,
                start_date=start_date,
                end_date=end_date,
                date_type=date_type,
                taxonomy_terms=taxonomy_terms,
                vocabularies=vocabularies,
            ),
        )

    def get(
        self,
        archive_id: int,
        *,
        locale: str = "es",
        date: str | None = None,
        taxonomy_terms: list[str] | None = None,
        vocabularies: list[str] | None = None,
    ) -> dict[str, Any]:
        return self.client.get(
            f"/archives/{archive_id}",
            params=_params(
                locale=locale,
                date=date,
                taxonomy_terms=taxonomy_terms,
                vocabularies=vocabularies,
            ),
        )

    def calculator_data(
        self,
        archive_id: int,
        *,
        start_date: str,
        end_date: str,
        locale: str = "es",
        taxonomy_terms: list[str] | None = None,
        vocabularies: list[str] | None = None,
    ) -> dict[str, Any]:
        return self.client.get(
            f"/calculator-data/{archive_id}",
            params=_params(
                locale=locale,
                start_date=start_date,
                end_date=end_date,
                taxonomy_terms=taxonomy_terms,
                vocabularies=vocabularies,
            ),
        )

    def download(
        self,
        archive_id: int,
        *,
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        date_type: str | None = None,
        locale: str = "es",
    ) -> tuple[bytes, str | None]:
        return self.client.download(
            f"/archives/{archive_id}/download",
            params=_params(
                locale=locale,
                date=date,
                start_date=start_date,
                end_date=end_date,
                date_type=date_type,
            ),
        )

    def list_json(
        self,
        *,
        locale: str = "es",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        taxonomy_terms: list[str] | None = None,
        vocabularies: list[str] | None = None,
    ) -> dict[str, Any]:
        return self.client.get(
            "/archives_json",
            params=_params(
                locale=locale,
                date=date,
                start_date=start_date,
                end_date=end_date,
                taxonomy_terms=taxonomy_terms,
                vocabularies=vocabularies,
            ),
        )

    def get_json_archive(
        self,
        archive_id: int,
        *,
        locale: str = "es",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        taxonomy_terms: list[str] | None = None,
        vocabularies: list[str] | None = None,
    ) -> dict[str, Any]:
        return self.client.get(
            f"/archives/{archive_id}",
            params=_params(
                locale=locale,
                date=date,
                start_date=start_date,
                end_date=end_date,
                taxonomy_terms=taxonomy_terms,
                vocabularies=vocabularies,
            ),
        )

    def download_json(
        self,
        archive_id: int,
        *,
        locale: str = "es",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        taxonomy_terms: list[str] | None = None,
        vocabularies: list[str] | None = None,
    ) -> Any:
        return self.client.get_json(
            f"/archives/{archive_id}/download_json",
            params=_params(
                locale=locale,
                date=date,
                start_date=start_date,
                end_date=end_date,
                taxonomy_terms=taxonomy_terms,
                vocabularies=vocabularies,
            ),
        )
