"""Generic REData API tool."""

from datetime import datetime
from typing import Optional

from ._common import build_data_request, fetch_json, json_result


def ree_data(
    category: str,
    widget: str,
    start_date: str,
    end_date: str,
    time_trunc: str = "day",
    lang: str = "es",
    geo_trunc: Optional[str] = None,
    geo_limit: Optional[str] = None,
    geo_ids: Optional[str] = None,
) -> str:
    """
    Retrieve a REData widget from Red Electrica's public API.

    Use the widget names listed in the REData API documentation, for example
    category='balance', widget='balance-electrico'. Dates use the API's local
    Spanish time convention and must be ISO datetimes such as 2024-01-01T00:00.
    For geographic requests, geo_trunc must be 'electric_system', geo_limit
    selects the system type (for example 'ccaa'), and geo_ids is its numeric ID.
    The demanda-tiempo-real widget is national-only and cannot be filtered by
    autonomous community.
    """
    url, params = build_data_request(
        lang,
        category,
        widget,
        start_date,
        end_date,
        time_trunc,
        geo_trunc,
        geo_limit,
        geo_ids,
    )
    payload = fetch_json(url, params)
    return json_result(
        {
            "source": "REE",
            "service": "REData API",
            "lang": lang,
            "category": category,
            "widget": widget,
            "start_date": params["start_date"],
            "end_date": params["end_date"],
            "time_trunc": time_trunc,
            "retrieved_at": datetime.now().isoformat(),
        },
        payload,
    )
