"""LLM-facing e·sios MCP tools."""

from .archives import (
    esios_download_archive,
    esios_download_json_archive,
    esios_get_archive,
    esios_get_archive_calculator_data,
    esios_get_json_archive,
    esios_list_archives,
    esios_list_json_archives,
)
from .auctions import esios_list_auctions
from .content import esios_filter_news, esios_get_content, esios_get_content_by_id, esios_list_content
from .indicators import esios_get_indicator, esios_list_indicators, esios_search_indicators
from .offers import esios_get_offer_indicator, esios_get_offer_widget
from .search import esios_search_contents, esios_search_contents_and_indicators
from .widgets import esios_get_widget, esios_list_widgets

__all__ = [
    "esios_download_archive",
    "esios_download_json_archive",
    "esios_get_archive",
    "esios_get_archive_calculator_data",
    "esios_get_json_archive",
    "esios_list_archives",
    "esios_list_json_archives",
    "esios_list_auctions",
    "esios_filter_news",
    "esios_get_content",
    "esios_get_content_by_id",
    "esios_list_content",
    "esios_get_indicator",
    "esios_list_indicators",
    "esios_search_indicators",
    "esios_get_widget",
    "esios_list_widgets",
    "esios_get_offer_indicator",
    "esios_get_offer_widget",
    "esios_search_contents",
    "esios_search_contents_and_indicators",
]
