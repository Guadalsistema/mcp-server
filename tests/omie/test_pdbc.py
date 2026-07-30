import json
import os
import unittest

from omie_mcp.tools.marginalpdbc import marginalpdbc
from omie_mcp.tools.pdbc import pdbc


@unittest.skipUnless(os.getenv("LIVE_TEST") == "1", "set LIVE_TEST=1 to run live OMIE integration tests")
class MarginalPdbcTests(unittest.TestCase):
    def test_fetches_may_2020_date(self):
        result = json.loads(marginalpdbc(since="2024-05-01", until="2024-05-01"))

        self.assertEqual(result["metadata"]["product"], "marginalpdbc")
        self.assertEqual(result["metadata"]["since"], "2024-05-01")
        self.assertEqual(result["metadata"]["until"], "2024-05-01")
        self.assertGreater(result["metadata"]["count"], 0)
        self.assertTrue(all(row["date"] == "2024-05-01" for row in result["data"]))
        self.assertTrue(all(row["currency"] == "EUR/MWh" for row in result["data"]))

@unittest.skipUnless(os.getenv("LIVE_TEST") == "1", "set LIVE_TEST=1 to run live OMIE integration tests")
class PdbcTests(unittest.TestCase):
    def test_fetches_may_2020_date(self):
        result = json.loads(pdbc(since="2024-05-01", until="2024-05-01"))

        self.assertEqual(result["metadata"]["product"], "pdbc")
        self.assertEqual(result["metadata"]["since"], "2024-05-01")
        self.assertEqual(result["metadata"]["until"], "2024-05-01")
        self.assertGreater(result["metadata"]["count"], 0)
        self.assertTrue(all(row["date"] == "2024-05-01" for row in result["data"]))
        self.assertTrue(all(row["power_unit"] == "MW" for row in result["data"]))

if __name__ == "__main__":
    unittest.main()
