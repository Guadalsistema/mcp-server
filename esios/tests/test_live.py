import os
import unittest
from pathlib import Path

from dotenv import load_dotenv

from esios_mcp.api import EsiosApiClient, IndicatorsApi, WidgetsApi


if os.getenv("LIVE_TEST") == "1":
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@unittest.skipUnless(
    os.getenv("LIVE_TEST") == "1",
    "set LIVE_TEST=1 to run live e·sios API tests",
)
class LiveApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.getenv("ESIOS_API_KEY"):
            raise unittest.SkipTest("ESIOS_API_KEY is not configured")
        cls.indicators = IndicatorsApi(EsiosApiClient())
        cls.widgets = WidgetsApi(EsiosApiClient())

    def test_list_and_get_indicator(self):
        payload = self.indicators.list(locale="es")
        self.assertIsInstance(payload.get("indicators"), list)
        self.assertTrue(payload["indicators"])

        indicator_id = payload["indicators"][0]["id"]
        detail = self.indicators.get(int(indicator_id), locale="es")
        self.assertIn("indicator", detail)

    def test_list_and_get_widget(self):
        payload = self.widgets.list(locale="es")
        self.assertIsInstance(payload.get("widgets"), list)
        self.assertTrue(payload["widgets"])

        first_widget = payload["widgets"][0]
        identifier = first_widget.get("id_widget") or first_widget.get("id")
        detail = self.widgets.get(identifier, locale="es")
        self.assertIn("widget", detail)


if __name__ == "__main__":
    unittest.main()
