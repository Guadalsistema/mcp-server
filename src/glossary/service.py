"""Deterministic glossary matching, versioning, and catalogue caching."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import re
import time
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from .models import (
    GlossaryCandidate,
    GlossaryCatalog,
    GlossaryEntry,
    GlossaryMatchType,
    GlossarySearchRequest,
    GlossarySearchResponse,
    GlossaryLanguage,
    GlossarySource,
)


CatalogLoader = Callable[[GlossaryLanguage], GlossaryCatalog]


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return " ".join(without_accents.split())


def _entry_payload(entry: GlossaryEntry) -> dict[str, object]:
    return {
        "aliases": sorted(normalize_text(alias) for alias in entry.aliases),
        "canonical_label": normalize_text(entry.canonical_label),
        "definition": normalize_text(entry.definition),
        "domain": entry.domain,
        "language": entry.language,
        "source": entry.source,
        "source_id": entry.source_id,
        "source_name": normalize_text(entry.source_name),
    }


def glossary_version(entries: Sequence[GlossaryEntry]) -> str:
    normalized = sorted(
        (_entry_payload(entry) for entry in entries),
        key=lambda item: json.dumps(
            item,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ),
    )
    content = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _entry_id(entry: GlossaryEntry) -> str:
    if entry.source_id is not None:
        return f"{entry.source}:{entry.language}:{entry.source_id}"

    slug = re.sub(r"[^a-z0-9]+", "-", normalize_text(entry.canonical_label)).strip("-")
    domain = entry.domain or "general"
    return f"{entry.source}:{entry.language}:{domain}:{slug}"


def _entry_meaning(entry: GlossaryEntry) -> str:
    return json.dumps(
        {
            "aliases": sorted(normalize_text(alias) for alias in entry.aliases),
            "definition": normalize_text(entry.definition),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _match_entry(
    entry: GlossaryEntry,
    lookup_forms: set[str],
) -> tuple[GlossaryMatchType, float] | None:
    label = normalize_text(entry.canonical_label)
    aliases = {normalize_text(alias) for alias in entry.aliases}
    definition = normalize_text(entry.definition)

    if label in lookup_forms:
        return GlossaryMatchType.EXACT, 1.0
    if aliases.intersection(lookup_forms):
        return GlossaryMatchType.ALIAS, 0.9
    label_tokens = set(label.split())
    if any(label.startswith(form) or form in label_tokens for form in lookup_forms):
        return GlossaryMatchType.PREFIX, 0.7
    if any(form in definition for form in lookup_forms):
        return GlossaryMatchType.DEFINITION, 0.5
    return None


def search_entries(
    entries: Sequence[GlossaryEntry],
    request: GlossarySearchRequest,
) -> list[GlossaryCandidate]:
    lookup_forms = {
        normalized
        for value in (request.query, *request.lookup_forms)
        if (normalized := normalize_text(value))
    }
    candidates: dict[str, GlossaryCandidate] = {}
    meanings_by_base_id: dict[str, set[str]] = {}
    for entry in entries:
        if entry.source_id is None:
            meanings_by_base_id.setdefault(_entry_id(entry), set()).add(
                _entry_meaning(entry)
            )

    for entry in entries:
        if entry.language != request.language:
            continue
        if request.domain is not None and entry.domain != request.domain:
            continue
        match = _match_entry(entry, lookup_forms)
        if match is None:
            continue

        candidate_id = _entry_id(entry)
        meaning = _entry_meaning(entry)
        if len(meanings_by_base_id.get(candidate_id, ())) > 1:
            meaning_digest = hashlib.sha256(meaning.encode("utf-8")).hexdigest()[:12]
            candidate_id = f"{candidate_id}:meaning-{meaning_digest}"
        match_type, score = match
        candidate = GlossaryCandidate(
            id=candidate_id,
            canonical_label=entry.canonical_label,
            definition=entry.definition,
            language=entry.language,
            domain=entry.domain,
            aliases=sorted(
                entry.aliases,
                key=lambda alias: (normalize_text(alias), alias),
            ),
            match_type=match_type,
            score=score,
            source=entry.source_name,
        )
        current = candidates.get(candidate_id)
        candidate_tie_breaker = (
            normalize_text(candidate.canonical_label),
            normalize_text(candidate.definition),
            tuple(normalize_text(alias) for alias in candidate.aliases),
            candidate.canonical_label,
            candidate.definition,
            tuple(candidate.aliases),
            candidate.source,
        )
        current_tie_breaker = (
            (
                normalize_text(current.canonical_label),
                normalize_text(current.definition),
                tuple(normalize_text(alias) for alias in current.aliases),
                current.canonical_label,
                current.definition,
                tuple(current.aliases),
                current.source,
            )
            if current is not None
            else None
        )
        if (
            current is None
            or candidate.score > current.score
            or (
                candidate.score == current.score
                and current_tie_breaker is not None
                and candidate_tie_breaker < current_tie_breaker
            )
        ):
            candidates[candidate_id] = candidate

    return sorted(
        candidates.values(),
        key=lambda candidate: (
            -candidate.score,
            normalize_text(candidate.canonical_label),
            candidate.id,
        ),
    )[: request.limit]


@dataclass(frozen=True)
class _CachedCatalog:
    catalog: GlossaryCatalog
    expires_at: float


class GlossaryService:
    def __init__(
        self,
        loaders: Mapping[GlossarySource, CatalogLoader],
        *,
        ttl_seconds: float = 3600,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not math.isfinite(ttl_seconds) or ttl_seconds <= 0:
            raise ValueError("Glossary cache TTL must be finite and greater than zero")
        self._loaders = dict(loaders)
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._cache: dict[tuple[GlossarySource, str], _CachedCatalog] = {}
        self._locks: dict[
            tuple[GlossarySource, str],
            tuple[asyncio.AbstractEventLoop, asyncio.Lock],
        ] = {}

    def clear_cache(self) -> None:
        self._cache.clear()
        self._locks.clear()

    async def _catalog(
        self, source: GlossarySource, language: GlossaryLanguage
    ) -> GlossaryCatalog:
        key = (source, language)
        cached = self._cache.get(key)
        if cached is not None and cached.expires_at > self._clock():
            return cached.catalog

        loop = asyncio.get_running_loop()
        lock_state = self._locks.get(key)
        if lock_state is None or lock_state[0] is not loop:
            lock = asyncio.Lock()
            self._locks[key] = (loop, lock)
        else:
            lock = lock_state[1]
        async with lock:
            cached = self._cache.get(key)
            if cached is not None and cached.expires_at > self._clock():
                return cached.catalog

            loader = self._loaders.get(source)
            if loader is None:
                raise ValueError(f"Unsupported glossary source: {source}")
            catalog = await asyncio.to_thread(loader, language)
            if catalog.source != source or catalog.language != language:
                raise ValueError(
                    f"{source} glossary adapter returned a catalogue for the wrong source or language"
                )
            self._cache[key] = _CachedCatalog(
                catalog=catalog,
                expires_at=self._clock() + self._ttl_seconds,
            )
            return catalog

    async def search(
        self,
        sources: Sequence[GlossarySource],
        request: GlossarySearchRequest,
    ) -> GlossarySearchResponse:
        if not sources:
            raise ValueError("At least one glossary source is required")
        catalogs = await asyncio.gather(
            *(self._catalog(source, request.language) for source in sources)
        )
        entries = [entry for catalog in catalogs for entry in catalog.entries]
        return GlossarySearchResponse(
            schema_version="1",
            query=request.query,
            language=request.language,
            domain=request.domain,
            glossary_version=glossary_version(entries),
            candidates=search_entries(entries, request),
            retrieved_at=min(catalog.retrieved_at for catalog in catalogs),
        )


def _load_ree(language: GlossaryLanguage) -> GlossaryCatalog:
    from ree.api import glossary as glossary_api

    return glossary_api.load_glossary(language)


def _load_esios(language: GlossaryLanguage) -> GlossaryCatalog:
    from esios.api import glossary as glossary_api

    return glossary_api.load_glossary(language)


DEFAULT_GLOSSARY_SERVICE = GlossaryService(
    {"ree": _load_ree, "esios": _load_esios},
    ttl_seconds=float(os.getenv("GLOSSARY_CACHE_TTL_SECONDS", "3600")),
)
