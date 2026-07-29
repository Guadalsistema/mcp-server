"""Framework-independent clients for the e·sios HTTP API."""

from .client import ESIOS_API_BASE_URL, EsiosApiClient, EsiosApiError
from .archives import ArchivesApi
from .auctions import AuctionsApi
from .cached_widgets import CachedWidgetsApi
from .content import CONTENT_TYPES, ContentApi
from .indicators import IndicatorsApi
from .offers import OfferIndicatorsApi, OfferWidgetsApi
from .search import SearchApi
from .widgets import WidgetsApi

__all__ = [
    "ESIOS_API_BASE_URL",
    "EsiosApiClient",
    "EsiosApiError",
    "ArchivesApi",
    "AuctionsApi",
    "CachedWidgetsApi",
    "CONTENT_TYPES",
    "ContentApi",
    "IndicatorsApi",
    "OfferIndicatorsApi",
    "OfferWidgetsApi",
    "SearchApi",
    "WidgetsApi",
]
