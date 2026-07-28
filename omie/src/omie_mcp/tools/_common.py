"""Shared helpers for OMIE tools."""

import io
import json
import logging
import zipfile
from datetime import date, datetime, timedelta
from typing import Optional

import requests


logger = logging.getLogger(__name__)

OMIE_FILE_URL = "https://www.omie.es/en/file-download"

# The files do not contain field names, so keep the official file-model names
# next to the parser instead of relying on positional fields in each tool.
COLUMN_MAPS = {
    "marginalpdbc": {
        0: "year",
        1: "month",
        2: "day",
        3: "period",
        4: "marginal_pt",
        5: "marginal_es",
    },
    "pdbc": {
        0: "year",
        1: "month",
        2: "day",
        3: "period",
        4: "unit_code",
        5: "assigned_power",
        6: "unused",
        7: "offer_type",
        8: "offer_number",
    },
}


def parse_date(value: str, field_name: str) -> date:
    """Parse an ISO date, retaining support for the former compact format."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO date in YYYY-MM-DD format")

    try:
        if len(value) == 8 and value.isdigit():
            return datetime.strptime(value, "%Y%m%d").date()
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be an ISO date in YYYY-MM-DD format"
        ) from error


def resolve_date_range(
    since: Optional[str], until: Optional[str]
) -> tuple[date, date]:
    """Resolve optional bounds into an inclusive date range."""
    if since:
        start_date = parse_date(since, "since")
    elif until:
        start_date = parse_date(until, "until")
    else:
        start_date = date.today() - timedelta(days=2)

    if until:
        end_date = parse_date(until, "until")
    elif since:
        end_date = start_date
    else:
        end_date = date.today()

    if start_date > end_date:
        raise ValueError("since must be on or before until")
    return start_date, end_date


def build_date_range(since: Optional[str], until: Optional[str]) -> list[str]:
    start_date, end_date = resolve_date_range(since, until)
    return [
        (start_date + timedelta(days=offset)).isoformat()
        for offset in range((end_date - start_date).days + 1)
    ]


def build_month_range(start_date: date, end_date: date) -> list[str]:
    """Return the YYYYMM archive names covering an inclusive date range."""
    month = date(start_date.year, start_date.month, 1)
    last_month = date(end_date.year, end_date.month, 1)
    months = []
    while month <= last_month:
        months.append(month.strftime("%Y%m"))
        if month.month == 12:
            month = date(month.year + 1, 1, 1)
        else:
            month = date(month.year, month.month + 1, 1)
    return months


def date_from_filename(filename: str) -> Optional[date]:
    """Extract an OMIE daily date from a filename such as pdbc_20250701.1."""
    token = filename.rsplit("/", 1)[-1].split(".", 1)[0].rsplit("_", 1)[-1]
    if len(token) != 8 or not token.isdigit():
        return None
    try:
        return datetime.strptime(token, "%Y%m%d").date()
    except ValueError:
        return None


def fetch_omie_data(parent: str, date_token: str) -> Optional[str]:
    """Download one daily OMIE file and return its text content."""
    filename = f"{parent}_{date_token}.1"
    try:
        response = requests.get(
            OMIE_FILE_URL,
            params={"parents": parent, "filename": filename},
            timeout=30,
        )
        if response.status_code == 200:
            return response.text
        logger.warning("Failed to fetch OMIE data for %s: %s", date_token, response.status_code)
    except requests.RequestException as error:
        logger.error("Error fetching OMIE data for %s: %s", date_token, error)
    return None


def fetch_omie_archive(parent: str, month: str) -> Optional[dict[str, str]]:
    """Download and decode one monthly OMIE ZIP archive."""
    filename = f"{parent}_{month}.zip"
    try:
        response = requests.get(
            OMIE_FILE_URL,
            params={"parents": parent, "filename": filename},
            timeout=60,
        )
        if response.status_code != 200:
            logger.warning("Failed to fetch OMIE archive for %s: %s", month, response.status_code)
            return None

        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            return {
                name: archive.read(name).decode("latin-1")
                for name in archive.namelist()
                if not name.endswith("/")
            }
    except (requests.RequestException, zipfile.BadZipFile, KeyError) as error:
        logger.error("Error fetching OMIE archive for %s: %s", month, error)
        return None


def _convert_value(field_name: str, value: str):
    if field_name in {"year", "month", "day", "period", "unused", "offer_type", "offer_number"}:
        return int(value)
    if field_name in {"marginal_pt", "marginal_es", "assigned_power"}:
        return float(value)
    return value


def parse_omie_csv(csv_content: str, format_name: str) -> list[dict]:
    """Parse an OMIE file, ignoring headers, empty lines, and malformed rows."""
    format_key = format_name.lower()
    try:
        column_map = COLUMN_MAPS[format_key]
    except KeyError as error:
        raise ValueError(f"Unsupported OMIE format: {format_name}") from error

    minimum_columns = max(column_map) + 1
    data = []
    for raw_line in csv_content.splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line:
            continue
        if line.startswith("*"):
            break

        parts = [part.strip() for part in line.split(";")]
        while parts and not parts[-1]:
            parts.pop()
        if len(parts) < minimum_columns or parts[0].upper() == format_key.upper():
            continue

        try:
            values = {
                name: _convert_value(name, parts[index])
                for index, name in column_map.items()
            }
            row_date = date(
                int(values["year"]), int(values["month"]), int(values["day"])
            )
        except (ValueError, TypeError, IndexError):
            continue

        values["date"] = row_date.isoformat()
        if format_key == "marginalpdbc":
            values["currency"] = "EUR/MWh"
        else:
            values["power_unit"] = "MW"
        data.append(values)

    return data


def filter_date_range(data: list[dict], start_date: date, end_date: date) -> list[dict]:
    """Keep only rows whose source date is within the requested range."""
    return [
        row
        for row in data
        if start_date.isoformat() <= row["date"] <= end_date.isoformat()
    ]


def build_result(
    product: str,
    since: str,
    until: str,
    data: list[dict],
    column_map: dict[int, str],
) -> str:
    result = {
        "metadata": {
            "source": "OMIE",
            "product": product,
            "since": since,
            "until": until,
            "retrieved_at": datetime.now().isoformat(),
            "count": len(data),
            "column_map": {str(index): name for index, name in column_map.items()},
        },
        "data": data,
    }
    return json.dumps(result, indent=2)
