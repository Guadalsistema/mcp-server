"""
Basic Matching Process Data Tool for OMIE
This tool provides access to OMIE's basic matching process data
"""

import json
import os
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)

def get_cache_connection():
    """Get connection to SQLite cache database."""
    cache_db = "omie_cache.db"
    conn = sqlite3.connect(cache_db, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS omie_cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            timestamp INTEGER,
            ttl INTEGER
        )
    """)
    return conn

def cache_get(key: str) -> Optional[str]:
    """Get cached value if not expired."""
    try:
        conn = get_cache_connection()
        cursor = conn.execute(
            "SELECT value, timestamp, ttl FROM omie_cache WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        if row:
            value, timestamp, ttl = row
            if datetime.now().timestamp() < timestamp + ttl:
                return value
        conn.close()
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

def cache_set(key: str, value: str, ttl: int = 3600):
    """Set cached value with TTL."""
    try:
        conn = get_cache_connection()
        timestamp = int(datetime.now().timestamp())
        conn.execute(
            "INSERT OR REPLACE INTO omie_cache VALUES (?, ?, ?, ?)",
            (key, value, timestamp, ttl)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Cache set error: {e}")

def _fetch_omie_data(date: str) -> Optional[str]:
    """Fetch OMIE data for a specific date."""
    try:
        url = f"https://www.omie.es/en/file-download?parents=pdbc&filename=pdbc_{date}.1"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            logger.warning(f"Failed to fetch OMIE data for {date}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching OMIE data for {date}: {e}")
        return None

def _parse_omie_csv(csv_content: str) -> list:
    """Parse OMIE CSV data into structured format."""
    data = []
    lines = csv_content.strip().split('\n')
    
    for line in lines:
        if line.startswith('*'):
            break
        if line.startswith('PDBC'):
            continue
            
        parts = line.split(';')
        if len(parts) >= 6:
            try:
                year, month, day, hour, price1, price2 = parts[:6]
                data.append({
                    "date": f"{year}{month.zfill(2)}{day.zfill(2)}",
                    "hour": int(hour),
                    "price1": float(price1) if price1 else 0.0,
                    "price2": float(price2) if price2 else 0.0,
                    "currency": "EUR/MWh"
                })
            except (ValueError, IndexError):
                continue
                
    return data

def pdbc(since: Optional[str] = None, until: Optional[str] = None) -> str:
    """
    Retrieve OMIE basic matching process data for the Spanish electricity market.
    
    Args:
        since: Start date in YYYYMMDD format (optional)
        until: End date in YYYYMMDD format (optional)
        
    Returns:
        JSON string containing the basic matching process data
    """
    # Generate cache key
    cache_key = f"pdbc_{since}_{until}"
    
    # Try to get from cache first
    cached_result = cache_get(cache_key)
    if cached_result:
        logger.info("Returning cached result")
        return cached_result
    
    # Prepare date range
    if since and until:
        # Generate a list of dates in range
        start_date = datetime.strptime(since, '%Y%m%d')
        end_date = datetime.strptime(until, '%Y%m%d')
        date_range = [(start_date + timedelta(days=i)).strftime('%Y%m%d') 
                     for i in range((end_date - start_date).days + 1)]
    elif since:
        # Single date
        date_range = [since]
    elif until:
        # Single date
        date_range = [until]
    else:
        # Default to recent dates
        today = datetime.now()
        date_range = [(today - timedelta(days=i)).strftime('%Y%m%d') for i in range(3)]
    
    # Collect data
    all_data = []
    for date_str in date_range:
        # Always fetch live data - server runs with live access enabled
        csv_content = _fetch_omie_data(date_str)
        if csv_content:
            parsed_data = _parse_omie_csv(csv_content)
            all_data.extend(parsed_data)
    
    # Create result
    result = {
        "metadata": {
            "source": "OMIE",
            "product": "pdbc",
            "since": since,
            "until": until,
            "retrieved_at": datetime.now().isoformat(),
            "count": len(all_data)
        },
        "data": all_data
    }
    
    # Cache the result
    result_json = json.dumps(result, indent=2)
    cache_set(cache_key, result_json, 3600)  # 1 hour TTL
    
    return result_json