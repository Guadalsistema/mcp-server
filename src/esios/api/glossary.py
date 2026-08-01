"""e·sios glossary endpoint and source-neutral response bridge."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from glossary.models import GlossaryCatalog, GlossaryEntry, GlossaryLanguage

from .client import EsiosApiClient, EsiosApiError
from .content import ContentApi


class _BodyTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.ignored_depth += 1
        elif not self.ignored_depth and tag in {"br", "li", "p"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.ignored_depth:
            self.ignored_depth -= 1
        elif not self.ignored_depth and tag in {"li", "p"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.ignored_depth:
            self.parts.append(data)


def _body_text(value: str) -> str:
    parser = _BodyTextParser()
    parser.feed(value)
    parser.close()
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()


def glossary_payload_to_catalog(
    payload: dict[str, Any],
    language: GlossaryLanguage,
    *,
    retrieved_at: datetime | None = None,
) -> GlossaryCatalog:
    """Bridge an e·sios `/glossaries` payload into searchable entries."""
    if language not in {"es", "en"}:
        raise ValueError("language must be one of: en, es")
    contents = payload.get("contents")
    if not isinstance(contents, list):
        raise EsiosApiError(
            "e·sios returned an invalid glossary response.",
            code="esios_invalid_response",
            retryable=True,
        )

    entries: list[GlossaryEntry] = []
    for index, content in enumerate(contents):
        if not isinstance(content, dict):
            raise EsiosApiError(
                f"e·sios glossary entry {index} has an invalid format.",
                code="esios_invalid_response",
                retryable=True,
            )
        source_id = content.get("id")
        title = content.get("title")
        body = content.get("body")
        definition = _body_text(body) if isinstance(body, str) else ""
        if (
            isinstance(source_id, bool)
            or not isinstance(source_id, (int, str))
            or not str(source_id).strip()
            or not isinstance(title, str)
            or not title.strip()
            or not definition
        ):
            raise EsiosApiError(
                f"e·sios glossary entry {index} is missing its id, title, or definition.",
                code="esios_invalid_response",
                retryable=True,
            )
        entries.append(
            GlossaryEntry(
                source="esios",
                source_name="e·sios glossary",
                source_id=str(source_id).strip(),
                canonical_label=title.strip(),
                definition=definition,
                language=language,
            )
        )

    if not entries:
        raise EsiosApiError(
            "e·sios glossary response did not contain any glossary entries.",
            code="esios_invalid_response",
            retryable=True,
        )
    return GlossaryCatalog(
        source="esios",
        language=language,
        entries=entries,
        retrieved_at=retrieved_at or datetime.now(timezone.utc),
    )


def load_glossary(
    language: GlossaryLanguage,
    *,
    api_key: str | None = None,
) -> GlossaryCatalog:
    """Fetch and adapt the complete localized e·sios glossary."""
    if language not in {"es", "en"}:
        raise ValueError("language must be one of: en, es")
    payload = ContentApi(EsiosApiClient(api_key=api_key)).list(
        "glossaries", locale=language
    )
    return glossary_payload_to_catalog(payload, language)
