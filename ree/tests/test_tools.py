import asyncio
import json
import unittest
from typing import cast
from unittest.mock import patch

from ree_mcp.app import server
from fastmcp.tools import ToolResult
from mcp.types import CallToolResult, TextContent
from ree_mcp.tools.data import ReeDataInput, ree_data
from ree_mcp.tools.glossary import parse_glossary_html, ree_glossary


DATA_PAYLOAD = {
    "data": {"type": "Evolucion de la demanda", "id": "dem1"},
    "included": [{"type": "Demanda", "attributes": {"values": []}}],
}

GLOSSARY_HTML = """
<div class="view-display-id-electric_terms">
  <div id="glossary-electric_terms-A" class="tab-pane">
    <div>
      <div class="views-field views-field-name"><span class="field-content">Almacenamiento</span></div>
      <div class="views-field views-field-description__value"><span class="field-content"><p>Instalacion que almacena energia.</p></span></div>
    </div>
  </div>
</div>
<div class="view-display-id-environmental_terms">
  <div id="glossary-environmental_terms-C" class="tab-pane">
    <div>
      <div class="views-field views-field-name"><span class="field-content">Campo electrico</span></div>
      <div class="views-field views-field-description__value"><span class="field-content">Descripcion ambiental.</span></div>
    </div>
  </div>
</div>
"""


class Response:
    status_code = 200
    text = ""

    def __init__(self, payload=None, text=""):
        self.payload = payload
        self.text = text

    def json(self):
        return self.payload


class DataToolTests(unittest.TestCase):
    def request(self, **overrides):
        values = {
            "category": "demanda",
            "widget": "evolucion",
            "start_date": "2024-01-01T00:00",
            "end_date": "2024-01-01T23:59",
        }
        values.update(overrides)
        return ReeDataInput.model_validate(values)

    @patch("ree_mcp.tools._common.requests.get")
    def test_ree_data_calls_api_and_preserves_payload(self, get):
        get.return_value = Response(DATA_PAYLOAD)

        result = json.loads(
            cast(str, ree_data(self.request()))
        )

        get.assert_called_once_with(
            "https://apidatos.ree.es/es/datos/demanda/evolucion",
            params={
                "start_date": "2024-01-01T00:00",
                "end_date": "2024-01-01T23:59",
                "time_trunc": "day",
            },
            headers={"Accept": "application/json"},
            timeout=60,
        )
        self.assertEqual(result["metadata"]["source"], "REE")
        self.assertEqual(result["data"], DATA_PAYLOAD)

    def test_rejects_partial_geography(self):
        with self.assertRaisesRegex(ValueError, "supplied together"):
            self.request(geo_limit="peninsular")

    def test_rejects_ccaa_as_geo_trunc(self):
        with self.assertRaisesRegex(ValueError, "Input should be 'electric_system'"):
            ReeDataInput.model_validate(
                {
                    "category": "demanda",
                    "widget": "evolucion",
                    "start_date": "2024-01-01T00:00",
                    "end_date": "2024-01-01T23:59",
                    "geo_trunc": "ccaa",
                    "geo_limit": "ccaa",
                    "geo_ids": "1",
                }
            )

    @patch("ree_mcp.tools._common.requests.get")
    def test_builds_official_regional_query(self, get):
        get.return_value = Response(DATA_PAYLOAD)

        ree_data(
            self.request(
                geo_trunc="electric_system",
                geo_limit="ccaa",
                geo_ids="1",
            )
        )

        get.assert_called_once_with(
            "https://apidatos.ree.es/es/datos/demanda/evolucion",
            params={
                "start_date": "2024-01-01T00:00",
                "end_date": "2024-01-01T23:59",
                "time_trunc": "day",
                "geo_trunc": "electric_system",
                "geo_limit": "ccaa",
                "geo_ids": "1",
            },
            headers={"Accept": "application/json"},
            timeout=60,
        )

    def test_rejects_wrong_category_for_instantaneous_power(self):
        with self.assertRaisesRegex(ValueError, "belongs to category generacion"):
            self.request(
                category="demanda",
                widget="potencia-maxima-instantanea",
            )

    @patch("ree_mcp.tools._common.requests.get")
    def test_fastmcp_rejects_english_category_before_api_call(self, get):
        tool = asyncio.run(server.get_tool("ree_data"))
        if tool is None:
            self.fail("ree_data tool was not registered")

        with self.assertRaisesRegex(Exception, "Input should be"):
            asyncio.run(
                tool.run(
                    {
                        "request": {
                            "category": "demand",
                            "widget": "potencia-maxima-instantanea",
                            "start_date": "2025-09-03T00:00",
                            "end_date": "2025-09-03T23:59",
                        }
                    }
                )
            )

        get.assert_not_called()

    @patch("ree_mcp.tools._common.requests.get")
    def test_fastmcp_requires_request_object(self, get):
        tool = asyncio.run(server.get_tool("ree_data"))
        if tool is None:
            self.fail("ree_data tool was not registered")

        with self.assertRaisesRegex(Exception, "Missing required argument"):
            asyncio.run(tool.run({}))

        get.assert_not_called()

    @patch("ree_mcp.tools._common.requests.get")
    def test_fastmcp_validates_before_making_invalid_request(self, get):
        tool = asyncio.run(server.get_tool("ree_data"))
        if tool is None:
            self.fail("ree_data tool was not registered")

        with self.assertRaisesRegex(Exception, "belongs to category generacion"):
            asyncio.run(
                tool.run(
                    {
                        "request": {
                            "category": "demanda",
                            "widget": "potencia-maxima-instantanea",
                            "start_date": "2025-09-03T00:00",
                            "end_date": "2025-09-03T23:59",
                            "geo_trunc": "electric_system",
                            "geo_limit": "ccaa",
                            "geo_ids": "6",
                        }
                    }
                )
            )

        get.assert_not_called()

    @patch("ree_mcp.tools._common.requests.get")
    def test_fastmcp_accepts_and_builds_andalusia_power_request(self, get):
        get.return_value = Response(DATA_PAYLOAD)
        tool = asyncio.run(server.get_tool("ree_data"))
        if tool is None:
            self.fail("ree_data tool was not registered")

        asyncio.run(
            tool.run(
                {
                    "request": {
                        "category": "generacion",
                        "widget": "potencia-maxima-instantanea",
                        "start_date": "2025-09-03T00:00",
                        "end_date": "2025-09-03T23:59",
                        "time_trunc": "day",
                        "geo_trunc": "electric_system",
                        "geo_limit": "ccaa",
                        "geo_ids": "6",
                    }
                }
            )
        )

        get.assert_called_once_with(
            "https://apidatos.ree.es/es/datos/generacion/potencia-maxima-instantanea",
            params={
                "start_date": "2025-09-03T00:00",
                "end_date": "2025-09-03T23:59",
                "time_trunc": "day",
                "geo_trunc": "electric_system",
                "geo_limit": "ccaa",
                "geo_ids": "6",
            },
            headers={"Accept": "application/json"},
            timeout=60,
        )

    @patch("ree_mcp.tools._common.requests.get")
    def test_upstream_failure_is_reported_as_mcp_tool_error(self, get):
        response = Response(text="<!doctype html><html><body>server error</body></html>")
        response.status_code = 500
        get.return_value = response

        result = asyncio.run(
            server.call_tool(
                "ree_data",
                {
                    "request": {
                        "category": "generacion",
                        "widget": "potencia-maxima-instantanea",
                        "start_date": "2026-02-12T00:00",
                        "end_date": "2026-02-12T23:59",
                        "geo_trunc": "electric_system",
                        "geo_limit": "ccaa",
                        "geo_ids": "6",
                    }
                },
            )
        )

        self.assertIsInstance(result, ToolResult)
        self.assertTrue(result.is_error)
        error_text = cast(TextContent, result.content[0]).text
        error = json.loads(error_text)
        self.assertEqual(error["error"]["code"], "ree_upstream_unavailable")
        self.assertTrue(error["error"]["retryable"])
        self.assertEqual(error["error"]["status_code"], 500)
        self.assertNotIn("<html>", error_text)
        wire_result = cast(CallToolResult, result.to_mcp_result())
        self.assertTrue(wire_result.isError)


class GlossaryToolTests(unittest.TestCase):
    def test_parser_extracts_both_categories(self):
        self.assertEqual(
            parse_glossary_html(GLOSSARY_HTML),
            [
                {
                    "category": "electrical",
                    "letter": "A",
                    "term": "Almacenamiento",
                    "definition": "Instalacion que almacena energia.",
                },
                {
                    "category": "environmental",
                    "letter": "C",
                    "term": "Campo electrico",
                    "definition": "Descripcion ambiental.",
                },
            ],
        )

    @patch("ree_mcp.tools.glossary._fetch_glossary", return_value=GLOSSARY_HTML)
    def test_glossary_search_is_accent_insensitive(self, fetch):
        result = json.loads(ree_glossary(term="almacenamiento", category="electrical"))

        fetch.assert_called_once_with("es")
        self.assertEqual(result["metadata"]["count"], 1)
        self.assertEqual(result["data"][0]["term"], "Almacenamiento")


if __name__ == "__main__":
    unittest.main()
