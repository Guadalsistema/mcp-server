import os
import unittest
from unittest.mock import MagicMock, patch

from esios_mcp.api import EsiosApiClient, IndicatorsApi, WidgetsApi


class Response:
    status_code = 200
    text = ""

    def __init__(self, payload=None, text=""):
        self.payload = payload
        self.text = text

    def json(self):
        return self.payload


class ApiClientTests(unittest.TestCase):
    def test_indicator_request_uses_versioned_headers_and_repeated_geo_ids(self):
        session = MagicMock()
        session.get.return_value = Response({"indicator": {"id": 123}})
        client = EsiosApiClient("secret", session=session)

        result = IndicatorsApi(client).get(
            123,
            locale="es",
            start_date="2025-01-01T00:00:00Z",
            end_date="2025-01-01T01:00:00Z",
            geo_ids=[1, 2],
        )

        self.assertEqual(result, {"indicator": {"id": 123}})
        session.get.assert_called_once_with(
            "https://api.esios.ree.es/indicators/123",
            params={
                "locale": "es",
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-01-01T01:00:00Z",
                "time_agg": "sum",
                "geo_agg": "sum",
                "geo_ids[]": ["1", "2"],
            },
            headers={
                "Accept": "application/json; application/vnd.esios-api-v1+json",
                "Content-Type": "application/json",
                "x-api-key": "secret",
            },
            timeout=60,
        )

    def test_widget_slug_is_quoted_and_uses_v2_headers(self):
        session = MagicMock()
        session.get.return_value = Response({"widget": {"id": "balance-electrico"}})
        client = EsiosApiClient("secret", session=session)

        WidgetsApi(client).get("balance-electrico", locale="en")

        session.get.assert_called_once_with(
            "https://api.esios.ree.es/widgets/balance-electrico",
            params={"locale": "en"},
            headers={
                "Accept": "application/json; application/vnd.esios-api-v2+json",
                "Content-Type": "application/json",
                "x-api-key": "secret",
            },
            timeout=60,
        )

    def test_missing_api_key_fails_fast(self):
        with patch.dict(os.environ, {"ESIOS_API_KEY": ""}):
            with self.assertRaisesRegex(Exception, "ESIOS_API_KEY"):
                EsiosApiClient(api_key="")


if __name__ == "__main__":
    unittest.main()
