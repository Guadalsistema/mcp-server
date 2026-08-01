"""REE glossary resource parsing and retrieval."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import TypedDict, cast

import requests

from glossary.models import (
    GlossaryCatalog,
    GlossaryDomain,
    GlossaryEntry,
    GlossaryLanguage,
)

from .client import REE_GLOSSARY_URLS, VALID_LANGUAGES


class _Field(TypedDict):
    kind: str
    depth: int
    parts: list[str]


class _GlossaryParser(HTMLParser):
    """Parse the two Drupal glossary views without an HTML dependency."""

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.category: str | None = None
        self.category_depth: int | None = None
        self.letter: str | None = None
        self.letter_depth: int | None = None
        self.field: _Field | None = None
        self.current_term: str | None = None
        self.records: list[dict[str, str]] = []

    @staticmethod
    def _clean(parts: list[str]) -> str:
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag not in self.VOID_TAGS:
            self.stack.append(tag)
        depth = len(self.stack)

        if "view-display-id-electric_terms" in classes:
            self.category = "electrical"
            self.category_depth = depth
        elif "view-display-id-environmental_terms" in classes:
            self.category = "environmental"
            self.category_depth = depth

        if tag == "div" and "tab-pane" in classes:
            pane_id = attributes.get("id") or ""
            for category, prefix in (
                ("electrical", "glossary-electric_terms-"),
                ("environmental", "glossary-environmental_terms-"),
            ):
                if pane_id.startswith(prefix):
                    self.letter = pane_id[len(prefix) :]
                    self.letter_depth = depth
                    break

        if self.category and self.letter and tag == "div":
            if "views-field-name" in classes:
                self.field = {"kind": "term", "depth": depth, "parts": []}
            elif "views-field-description__value" in classes:
                self.field = {"kind": "definition", "depth": depth, "parts": []}

        if self.field and tag in {"br", "p"}:
            self.field["parts"].append("\n")

    def handle_data(self, data: str) -> None:
        if self.field:
            self.field["parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "br"} and self.field:
            self.field["parts"].append("\n")

        if self.field and tag == "div" and len(self.stack) == self.field["depth"]:
            value = self._clean(self.field["parts"])
            if self.field["kind"] == "term":
                self.current_term = value
            elif self.field["kind"] == "definition" and self.current_term:
                self.records.append(
                    {
                        "category": self.category or "",
                        "letter": self.letter or "",
                        "term": self.current_term,
                        "definition": value,
                    }
                )
                self.current_term = None
            self.field = None

        if self.letter and tag == "div" and len(self.stack) == self.letter_depth:
            self.letter = None
        if self.category and tag == "div" and len(self.stack) == self.category_depth:
            self.category = None
        if tag not in self.VOID_TAGS and self.stack:
            self.stack.pop()

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def parse_glossary_html(html: str) -> list[dict[str, str]]:
    parser = _GlossaryParser()
    parser.feed(html)
    parser.close()
    return parser.records


def _fetch_glossary(lang: str) -> str:
    try:
        response = requests.get(
            REE_GLOSSARY_URLS[lang],
            headers={"Accept": "text/html"},
            timeout=60,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"REE glossary request failed: {error}") from error
    if response.status_code >= 400:
        raise RuntimeError(
            f"REE glossary request failed with HTTP {response.status_code}: "
            f"{response.text.strip() or 'no response body'}"
        )
    return response.text


def glossary_records_to_catalog(
    records: list[dict[str, str]],
    language: GlossaryLanguage,
    *,
    retrieved_at: datetime | None = None,
) -> GlossaryCatalog:
    """Bridge parsed REE records into the source-neutral glossary catalogue."""
    if language not in VALID_LANGUAGES:
        raise ValueError("language must be one of: en, es")
    entries = [
        GlossaryEntry(
            source="ree",
            source_name="REE glossary",
            canonical_label=record["term"],
            definition=record["definition"],
            language=language,
            domain=cast(GlossaryDomain, record["category"]),
        )
        for record in records
    ]
    return GlossaryCatalog(
        source="ree",
        language=language,
        entries=entries,
        retrieved_at=retrieved_at or datetime.now(timezone.utc),
    )


def load_glossary(language: GlossaryLanguage) -> GlossaryCatalog:
    """Fetch and adapt the complete localized REE glossary."""
    if language not in VALID_LANGUAGES:
        raise ValueError("language must be one of: en, es")
    records = parse_glossary_html(_fetch_glossary(language))
    if not records:
        raise RuntimeError("REE glossary response did not contain any glossary entries")
    return glossary_records_to_catalog(records, language)
