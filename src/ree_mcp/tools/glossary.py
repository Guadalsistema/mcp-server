"""REE glossary retrieval and search tool."""

from __future__ import annotations

import asyncio
import re
import unicodedata
from datetime import datetime
from html.parser import HTMLParser
from typing import Optional, TypedDict

from fastmcp import Context
import requests

from ._common import REE_GLOSSARY_URLS, VALID_LANGUAGES, json_result, mcp_log


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


def _search_key(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(character)
    )


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


async def ree_glossary(
    term: Optional[str] = None,
    category: Optional[str] = None,
    lang: str = "es",
    ctx: Context | None = None,
) -> str:
    # TODO improve the tool description and explain the expected usage
    """
    Search REE's electrical and environmental glossary.

    Matching is case- and accent-insensitive and searches both terms and
    definitions. Leave term empty to retrieve all glossary entries.
    """
    if lang not in VALID_LANGUAGES:
        raise ValueError("lang must be one of: en, es")
    if category not in {None, "electrical", "environmental"}:
        raise ValueError("category must be electrical or environmental")
    if term is not None and not isinstance(term, str):
        raise ValueError("term must be a string")

    url = REE_GLOSSARY_URLS[lang]
    await mcp_log(
        ctx,
        "Calling the REE glossary API",
        extra={"url": url, "lang": lang},
    )
    try:
        html = await asyncio.to_thread(_fetch_glossary, lang)
    except RuntimeError as error:
        await mcp_log(
            ctx,
            "REE glossary API call failed",
            level="error",
            extra={"url": url, "error_type": type(error).__name__},
        )
        raise

    records = parse_glossary_html(html)
    if category:
        records = [record for record in records if record["category"] == category]
    if term:
        needle = _search_key(term)
        records = [
            record
            for record in records
            if needle in _search_key(record["term"])
            or needle in _search_key(record["definition"])
        ]

    await mcp_log(
        ctx,
        "REE glossary API call completed",
        extra={"url": url, "status": "success", "result_count": len(records)},
    )
    return json_result(
        {
            "source": "REE",
            "service": "REE glossary",
            "lang": lang,
            "category": category,
            "term": term,
            "count": len(records),
            "retrieved_at": datetime.now().isoformat(),
        },
        records,
    )
