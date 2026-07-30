"""
Marginal Price Data Tool for OMIE
This tool maps OMIE CSV files to MCP tools that return JSON data
"""

from datetime import timedelta
from typing import Optional

from ._common import (
    COLUMN_MAPS,
    build_result,
    fetch_omie_data,
    filter_date_range,
    parse_omie_csv,
    resolve_date_range,
)


def marginalpdbc(since: Optional[str] = None, until: Optional[str] = None) -> str:
    """
    Retrieve hourly prices for Spain's day-ahead market.
    Precios horarios del mercado diario en España.
    """
    start_date, end_date = resolve_date_range(since, until)
    all_data = []
    current_date = start_date
    while current_date <= end_date:
        date_token = current_date.strftime("%Y%m%d")
        csv_content = fetch_omie_data("marginalpdbc", date_token)
        if csv_content:
            all_data.extend(parse_omie_csv(csv_content, "marginalpdbc"))
        current_date += timedelta(days=1)

    return build_result(
        "marginalpdbc",
        start_date.isoformat(),
        end_date.isoformat(),
        filter_date_range(all_data, start_date, end_date),
        COLUMN_MAPS["marginalpdbc"],
    )
