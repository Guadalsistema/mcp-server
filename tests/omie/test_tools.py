import importlib
import json
import unittest
from unittest.mock import patch

from omie.tools._common import build_date_range, parse_omie_csv


marginalpdbc_module = importlib.import_module("omie.tools.marginalpdbc")
pdbc_module = importlib.import_module("omie.tools.pdbc")


MARGINAL_FILE = """MARGINALPDBC;
2025;07;01;1;129.98;129.98;
2025;07;02;2;118.32;118.32;
*
"""

PDBC_FILE = """PDBC;
2025;07;01;1;ABOUC01;-2.1;0;1;9757248;
2025;07;02;1;ABOX;-1.8;0;1;9766389;
*
"""


class CommonToolTests(unittest.TestCase):
    def test_build_date_range_accepts_iso_dates(self):
        self.assertEqual(
            build_date_range("2025-07-31", "2025-08-02"),
            ["2025-07-31", "2025-08-01", "2025-08-02"],
        )

    def test_parse_marginal_file_uses_named_columns_and_discards_header(self):
        rows = parse_omie_csv(MARGINAL_FILE, "marginalpdbc")

        self.assertEqual(
            rows,
            [
                {
                    "year": 2025,
                    "month": 7,
                    "day": 1,
                    "period": 1,
                    "marginal_pt": 129.98,
                    "marginal_es": 129.98,
                    "date": "2025-07-01",
                    "currency": "EUR/MWh",
                },
                {
                    "year": 2025,
                    "month": 7,
                    "day": 2,
                    "period": 2,
                    "marginal_pt": 118.32,
                    "marginal_es": 118.32,
                    "date": "2025-07-02",
                    "currency": "EUR/MWh",
                },
            ],
        )

    def test_parse_pdbc_file_uses_named_columns_and_discards_header(self):
        rows = parse_omie_csv(PDBC_FILE, "PDBC")

        self.assertEqual(rows[0], {
            "year": 2025,
            "month": 7,
            "day": 1,
            "period": 1,
            "unit_code": "ABOUC01",
            "assigned_power": -2.1,
            "unused": 0,
            "offer_type": 1,
            "offer_number": 9757248,
            "date": "2025-07-01",
            "power_unit": "MW",
        })


class ToolRangeTests(unittest.TestCase):
    def test_marginalpdbc_downloads_each_requested_daily_file(self):
        files = {
            "20250731": MARGINAL_FILE.replace("2025;07;01", "2025;07;31"),
            "20250801": MARGINAL_FILE.replace("2025;07;01", "2025;08;01"),
        }

        with patch.object(
            marginalpdbc_module,
            "fetch_omie_data",
            side_effect=lambda parent, token: files[token],
        ) as fetch:
            result = json.loads(
                marginalpdbc_module.marginalpdbc("2025-07-31", "2025-08-01")
            )

        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(result["metadata"]["since"], "2025-07-31")
        self.assertEqual(result["metadata"]["until"], "2025-08-01")
        self.assertTrue(all(row["date"] in {"2025-07-31", "2025-08-01"} for row in result["data"]))

    def test_pdbc_downloads_one_archive_per_month_and_filters_rows(self):
        archives = {
            "202507": {
                "pdbc_20250731.1": PDBC_FILE.replace("2025;07;01", "2025;07;31")
            },
            "202508": {
                "pdbc_20250801.1": PDBC_FILE.replace("2025;07;01", "2025;08;01")
            },
        }

        with patch.object(
            pdbc_module,
            "fetch_omie_archive",
            side_effect=lambda parent, month: archives[month],
        ) as fetch:
            result = json.loads(
                pdbc_module.pdbc("2025-07-31", "2025-08-01")
            )

        self.assertEqual([call.args[1] for call in fetch.call_args_list], ["202507", "202508"])
        self.assertEqual(
            {row["date"] for row in result["data"]},
            {"2025-07-31", "2025-08-01"},
        )
        self.assertEqual(result["metadata"]["column_map"]["5"], "assigned_power")


if __name__ == "__main__":
    unittest.main()
