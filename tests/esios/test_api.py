import os
import unittest
from unittest.mock import MagicMock, patch

from esios_mcp.api import (
    ArchivesApi,
    CachedWidgetsApi,
    ContentApi,
    EsiosApiClient,
    IndicatorsApi,
    WidgetsApi,
)


class Response:
    status_code = 200
    text = ""

    def __init__(self, payload=None, text=""):
        self.payload = payload
        self.text = text

    def json(self):
        return self.payload


class ApiClientTests(unittest.TestCase):
    def test_indicator_filters_use_repeated_taxonomy_parameters(self):
        session = MagicMock()
        session.get.return_value = Response({"indicators": []})
        client = EsiosApiClient("secret", session=session)

        IndicatorsApi(client).search(
            "precio",
            locale="es",
            taxonomy_terms=["Potencia"],
            taxonomy_ids=[1, 2],
        )

        self.assertEqual(
            session.get.call_args.kwargs["params"],
            {
                "locale": "es",
                "taxonomy_terms[]": ["Potencia"],
                "taxonomy_ids[]": ["1", "2"],
                "text": "precio",
            },
        )

    def test_cached_widget_uses_v2_headers(self):
        session = MagicMock()
        session.get.return_value = Response({"widget": {"id_widget": 1}})
        client = EsiosApiClient("secret", session=session)

        CachedWidgetsApi(client).get(1, locale="en")

        session.get.assert_called_once_with(
            "https://api.esios.ree.es/cached_widgets/1",
            params={"locale": "en"},
            headers={
                "Accept": "application/json; application/vnd.esios-api-v2+json",
                "Content-Type": "application/json",
                "x-api-key": "secret",
            },
            timeout=60,
        )

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

    def test_archive_filters_use_repeated_query_parameters(self):
        session = MagicMock()
        session.get.return_value = Response({"archives": []})
        client = EsiosApiClient("secret", session=session)

        ArchivesApi(client).list(
            locale="es",
            start_date="2025-01-01T00:00:00Z",
            end_date="2025-01-02T00:00:00Z",
            date_type="datos",
            taxonomy_terms=["Potencia"],
            vocabularies=["Mercado"],
        )

        session.get.assert_called_once_with(
            "https://api.esios.ree.es/archives",
            params={
                "locale": "es",
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-01-02T00:00:00Z",
                "date_type": "datos",
                "taxonomy_terms[]": ["Potencia"],
                "vocabularies[]": ["Mercado"],
            },
            headers={
                "Accept": "application/json; application/vnd.esios-api-v1+json",
                "Content-Type": "application/json",
                "x-api-key": "secret",
            },
            timeout=60,
        )

    def test_content_by_id_uses_contents_route(self):
        session = MagicMock()
        session.get.return_value = Response({"content": {"id": 123}})
        client = EsiosApiClient("secret", session=session)

        result = ContentApi(client).get_by_id(123, locale="en")

        self.assertEqual(result, {"content": {"id": 123}})
        self.assertEqual(session.get.call_args.args[0], "https://api.esios.ree.es/contents/123")
        self.assertEqual(session.get.call_args.kwargs["params"], {"locale": "en"})

    def test_json_and_binary_responses_are_supported(self):
        session = MagicMock()
        json_response = Response([{"Indicadores": "Precio"}])
        binary_response = Response({})
        binary_response.content = b"pdf-bytes"
        binary_response.headers = {"Content-Type": "application/pdf"}
        session.get.side_effect = [json_response, binary_response]
        client = EsiosApiClient("secret", session=session)

        self.assertEqual(client.get_json("/archives/1/download_json"), [{"Indicadores": "Precio"}])
        content, content_type = client.download("/archives/1/download")
        self.assertEqual(content, b"pdf-bytes")
        self.assertEqual(content_type, "application/pdf")


if __name__ == "__main__":
    unittest.main()
