"""
Basic Matching Process Data Tool for OMIE
This tool provides access to OMIE's basic matching process data
"""

from typing import Optional

from ._common import (
    COLUMN_MAPS,
    build_month_range,
    build_result,
    date_from_filename,
    fetch_omie_archive,
    filter_date_range,
    parse_omie_csv,
    resolve_date_range,
)


def pdbc(since: Optional[str] = None, until: Optional[str] = None) -> str:
    """
    Retrieve Spain's daily base matching schedule.
    Programa diario base de casación español.
    """
    start_date, end_date = resolve_date_range(since, until)
    all_data = []
    for month in build_month_range(start_date, end_date):
        archive = fetch_omie_archive("pdbc", month)
        if not archive:
            continue
        for filename, csv_content in archive.items():
            file_date = date_from_filename(filename)
            if file_date is None or not start_date <= file_date <= end_date:
                continue
            all_data.extend(parse_omie_csv(csv_content, "pdbc"))

    return build_result(
        "pdbc",
        start_date.isoformat(),
        end_date.isoformat(),
        filter_date_range(all_data, start_date, end_date),
        COLUMN_MAPS["pdbc"],
    )
