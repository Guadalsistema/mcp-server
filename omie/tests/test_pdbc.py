import json
import os
import unittest

from omie_mcp.tools.marginalpdbc import marginalpdbc


@unittest.skipUnless(os.getenv("LIVE_TEST") == "1", "set LIVE_TEST=1 to run live OMIE integration tests")
class MarginalPdbcTests(unittest.TestCase):
    def test_fetches_may_2020_date(self):
        result = json.loads(marginalpdbc(since="20240501", until="20240501"))

        self.assertEqual(result["metadata"]["product"], "marginalpdbc")
        self.assertEqual(result["metadata"]["since"], "20240501")
        self.assertEqual(result["metadata"]["until"], "20240501")
        self.assertGreater(result["metadata"]["count"], 0)
        self.assertTrue(all(row["date"] == "20240501" for row in result["data"]))
        self.assertTrue(all(row["currency"] == "EUR/MWh" for row in result["data"]))

@unittest.skipUnless(os.getenv("LIVE_TEST") == "1", "set LIVE_TEST=1 to run live OMIE integration tests")
class MarginalPdbcTests(unittest.TestCase):
    def test_fetches_may_2020_date(self):
        result = json.loads(pdbc(since="20240501", until="20240501"))

        self.assertEqual(result["metadata"]["product"], "pdbc")
        self.assertEqual(result["metadata"]["since"], "20240501")
        self.assertEqual(result["metadata"]["until"], "20240501")
        self.assertGreater(result["metadata"]["count"], 0)
        self.assertTrue(all(row["date"] == "20240501" for row in result["data"]))
        self.assertTrue(all(row["currency"] == "EUR/MWh" for row in result["data"]))

if __name__ == "__main__":
    unittest.main()
