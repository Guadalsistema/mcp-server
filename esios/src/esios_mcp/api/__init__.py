"""Framework-independent clients for the e·sios HTTP API."""

from .client import ESIOS_API_BASE_URL, EsiosApiClient, EsiosApiError
from .indicators import IndicatorsApi
from .widgets import WidgetsApi

__all__ = [
    "ESIOS_API_BASE_URL",
    "EsiosApiClient",
    "EsiosApiError",
    "IndicatorsApi",
    "WidgetsApi",
]
