import json
import os
import unittest

from ree_mcp.tools.data import ree_data
from ree_mcp.tools.glossary import ree_glossary


@unittest.skipUnless(
    os.getenv("LIVE_TEST") == "1",
    "set LIVE_TEST=1 to run live REE integration tests",
)
class ReeDataLiveTests(unittest.TestCase):
    def test_fetches_live_generation_widget(self):
        result = json.loads(
            ree_data(
                category="generacion",
                widget="estructura-generacion",
                start_date="2019-01-01T00:00",
                end_date="2019-01-01T23:59",
                time_trunc="day",
            )
        )

        self.assertEqual(result["metadata"]["source"], "REE")
        self.assertEqual(result["metadata"]["category"], "generacion")
        self.assertEqual(result["metadata"]["widget"], "estructura-generacion")
        self.assertIn("included", result["data"])
        self.assertGreater(len(result["data"]["included"]), 0)


@unittest.skipUnless(
    os.getenv("LIVE_TEST") == "1",
    "set LIVE_TEST=1 to run live REE integration tests",
)
class ReeGlossaryLiveTests(unittest.TestCase):
    def test_fetches_live_glossary_term(self):
        result = json.loads(ree_glossary(term="Almacenamiento", category="electrical"))

        self.assertGreater(result["metadata"]["count"], 0)
        self.assertTrue(
            any(item["term"] == "Almacenamiento" for item in result["data"])
        )


if __name__ == "__main__":
    unittest.main()
