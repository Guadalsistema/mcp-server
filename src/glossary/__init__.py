"""Shared glossary contracts and search behavior."""

from .models import (
    GlossaryCandidate,
    GlossaryCatalog,
    GlossaryEntry,
    GlossaryMatchType,
    GlossarySearchRequest,
    GlossarySearchResponse,
)

__all__ = [
    "GlossaryCandidate",
    "GlossaryCatalog",
    "GlossaryEntry",
    "GlossaryMatchType",
    "GlossarySearchRequest",
    "GlossarySearchResponse",
]
