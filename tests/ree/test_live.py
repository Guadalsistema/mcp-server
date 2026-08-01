import asyncio
import json
import os
import unittest
from typing import cast

from ree.mcp.data import ReeDataInput, ree_data
from ree.mcp.glossary import ree_glossary_search
from glossary.models import GlossarySearchRequest


@unittest.skipUnless(
    os.getenv("LIVE_TEST") == "1",
    "set LIVE_TEST=1 to run live REE integration tests",
)
class ReeDataLiveTests(unittest.TestCase):
    def test_fetches_live_generation_widget(self):
        raw_result = asyncio.run(
            ree_data(
                ReeDataInput(
                    category="generacion",
                    widget="estructura-generacion",
                    start_date="2019-01-01T00:00",
                    end_date="2019-01-01T23:59",
                    time_trunc="day",
                )
            )
        )
        result = json.loads(cast(str, raw_result))

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
    def test_fetches_live_structured_glossary_term(self):
        result = asyncio.run(
            ree_glossary_search(
                GlossarySearchRequest(
                    query="Almacenamiento",
                    lookup_forms=["almacenamiento"],
                    language="es",
                )
            )
        )

        self.assertTrue(result.candidates)
        self.assertEqual(result.candidates[0].source, "REE glossary")


if __name__ == "__main__":
    unittest.main()
