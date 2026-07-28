"""
Marginal Price Data Tool for OMIE
This tool maps OMIE CSV files to MCP tools that return JSON data
"""

from typing import Optional

from ._common import build_date_range, build_result, fetch_omie_data, parse_omie_csv


def marginalpdbc(since: Optional[str] = None, until: Optional[str] = None) -> str:
    """
    Retrieve OMIE marginal price data for the Spanish electricity market.
    """
    all_data = []
    for date_str in build_date_range(since, until):
        csv_content = fetch_omie_data("marginalpdbc", date_str)
        if csv_content:
            all_data.extend(parse_omie_csv(csv_content, "MARGINALPDBC"))

    return build_result("marginalpdbc", since, until, all_data)
