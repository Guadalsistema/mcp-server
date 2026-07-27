"""
Marginal Price Data Tool for OMIE
This tool maps OMIE CSV files to MCP tools that return JSON data
"""

import json
from datetime import datetime

def marginalpdbc(since=None, until=None):
    """
    Retrieve OMIE marginal price data for the Spanish electricity market.
    
    Args:
        since: Start date in YYYYMMDD format (optional)
        until: End date in YYYYMMDD format (optional)
        
    Returns:
        JSON string containing the marginal price data
    """
    # This simulates fetching data from OMIE's CSV files
    # In a real implementation, this would download and parse OMIE CSV files
    
    # Sample data structure
    sample_data = {
        "metadata": {
            "source": "OMIE",
            "product": "marginalpdbc",
            "since": since,
            "until": until,
            "retrieved_at": datetime.now().isoformat()
        },
        "data": [
            {
                "date": "20230307",
                "price": 52.34,
                "currency": "EUR/MWh"
            }
        ]
    }
    
    return json.dumps(sample_data, indent=2)