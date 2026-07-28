"""
Basic Matching Process Data Tool for OMIE
This tool provides access to OMIE's basic matching process data
"""

from typing import Optional

from ._common import build_date_range, build_result, fetch_omie_data, parse_omie_csv


def pdbc(since: Optional[str] = None, until: Optional[str] = None) -> str:
    """
    Retrieve OMIE basic matching process data for the Spanish electricity market.
    """
    all_data = []
    for date_str in build_date_range(since, until):
        csv_content = fetch_omie_data("pdbc", date_str)
        if csv_content:
            all_data.extend(parse_omie_csv(csv_content, "PDBC"))

    return build_result("pdbc", since, until, all_data)
