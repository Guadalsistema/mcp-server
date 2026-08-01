"""Typed contracts shared by glossary API adapters and MCP tools."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


GlossaryLanguage = Literal["es", "en"]
GlossaryDomain = Literal["electrical", "environmental"]
GlossarySource = Literal["ree", "esios"]
NonEmptyString = Annotated[str, Field(min_length=1)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class GlossarySearchRequest(Contract):
    query: str = Field(min_length=1)
    lookup_forms: list[NonEmptyString] = Field(min_length=1)
    language: GlossaryLanguage = "es"
    domain: GlossaryDomain | None = None
    limit: int = Field(default=10, ge=1, le=50)

    @field_validator("query")
    @classmethod
    def query_must_contain_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must contain non-whitespace characters")
        return value

    @field_validator("lookup_forms")
    @classmethod
    def lookup_forms_must_contain_text(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("lookup_forms must contain non-whitespace characters")
        return values


class GlossaryMatchType(StrEnum):
    EXACT = "exact"
    ALIAS = "alias"
    PREFIX = "prefix"
    DEFINITION = "definition"


class GlossaryCandidate(Contract):
    id: str = Field(min_length=1)
    canonical_label: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=8)
    domain: str | None = None
    aliases: list[str]
    match_type: GlossaryMatchType
    score: float = Field(ge=0, le=1)
    source: str = Field(min_length=1)


class GlossarySearchResponse(Contract):
    schema_version: Literal["1"]
    query: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=8)
    domain: str | None = None
    glossary_version: str = Field(min_length=1)
    candidates: list[GlossaryCandidate]
    retrieved_at: AwareDatetime


class GlossaryEntry(Contract):
    """Source-neutral entry returned by an API adapter."""

    source: GlossarySource
    source_name: str = Field(min_length=1)
    source_id: str | None = Field(default=None, min_length=1)
    canonical_label: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    language: GlossaryLanguage
    domain: GlossaryDomain | None = None
    aliases: list[str] = Field(default_factory=list)


class GlossaryCatalog(Contract):
    """Complete localized catalogue returned by an API adapter."""

    source: GlossarySource
    language: GlossaryLanguage
    entries: list[GlossaryEntry]
    retrieved_at: AwareDatetime
