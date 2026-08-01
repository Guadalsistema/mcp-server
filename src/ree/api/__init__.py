"""Framework-independent clients and resources for the REE APIs."""

from .client import (
    REE_API_BASE_URL,
    REE_GLOSSARY_URLS,
    ReeApiError,
    build_data_request,
    fetch_json,
)
from .glossary import glossary_records_to_catalog, load_glossary, parse_glossary_html

__all__ = [
    "REE_API_BASE_URL",
    "REE_GLOSSARY_URLS",
    "ReeApiError",
    "build_data_request",
    "fetch_json",
    "glossary_records_to_catalog",
    "load_glossary",
    "parse_glossary_html",
]
