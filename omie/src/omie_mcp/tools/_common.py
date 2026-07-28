"""Shared helpers for OMIE MCP tools."""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def build_date_range(since: Optional[str], until: Optional[str]) -> list[str]:
    if since and until:
        start_date = datetime.strptime(since, '%Y%m%d')
        end_date = datetime.strptime(until, '%Y%m%d')
        return [
            (start_date + timedelta(days=offset)).strftime('%Y%m%d')
            for offset in range((end_date - start_date).days + 1)
        ]
    if since:
        return [since]
    if until:
        return [until]

    today = datetime.now()
    return [(today - timedelta(days=offset)).strftime('%Y%m%d') for offset in range(3)]


def fetch_omie_data(parent: str, date: str) -> Optional[str]:
    try:
        url = f"https://www.omie.es/en/file-download?parents={parent}&filename={parent}_{date}.1"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.text
        logger.warning("Failed to fetch OMIE data for %s: %s", date, response.status_code)
        return None
    except Exception as error:
        logger.error("Error fetching OMIE data for %s: %s", date, error)
        return None


def parse_omie_csv(csv_content: str, header_prefix: str) -> list:
    data = []
    for line in csv_content.strip().split('\n'):
        if line.startswith('*'):
            break
        if line.startswith(header_prefix):
            continue

        parts = line.split(';')
        if len(parts) < 6:
            continue

        try:
            year, month, day, hour, price1, price2 = parts[:6]
            data.append({
                "date": f"{year}{month.zfill(2)}{day.zfill(2)}",
                "hour": int(hour),
                "price1": float(price1) if price1 else 0.0,
                "price2": float(price2) if price2 else 0.0,
                "currency": "EUR/MWh",
            })
        except (ValueError, IndexError):
            continue

    return data


def build_result(product: str, since: Optional[str], until: Optional[str], data: list) -> str:
    result = {
        "metadata": {
            "source": "OMIE",
            "product": product,
            "since": since,
            "until": until,
            "retrieved_at": datetime.now().isoformat(),
            "count": len(data),
        },
        "data": data,
    }
    return json.dumps(result, indent=2)
