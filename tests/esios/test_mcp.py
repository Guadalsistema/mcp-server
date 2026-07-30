import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp.tools import ToolResult
from mcp.types import TextContent

from esios_mcp.app import server
from esios_mcp.mcp.indicators import esios_get_indicator, esios_list_indicators
from esios_mcp.mcp.widgets import esios_get_widget


INDICATORS = {"indicators": [{"id": 123, "name": "Demanda"}], "meta": {"size": 1}}
WIDGET = {"widget": {"id_widget": 1, "id": "potencia", "indicators": []}}


class McpToolTests(unittest.TestCase):
    @patch("esios_mcp.mcp.indicators.EsiosApiClient")
    def test_list_indicators_preserves_upstream_payload(self, client_class):
        client = client_class.return_value
        client.get.return_value = INDICATORS

        result = json.loads(asyncio.run(esios_list_indicators()))

        self.assertEqual(result["data"], INDICATORS)
        self.assertEqual(result["metadata"]["request"], {"locale": "es"})
        client.get.assert_called_once()

    @patch("esios_mcp.mcp.indicators.EsiosApiClient")
    def test_indicator_reports_client_visible_notifications(self, client_class):
        client_class.return_value.get.return_value = {"indicator": {"id": 123}}
        ctx = MagicMock(request_context=object())
        ctx.info = AsyncMock()
        ctx.error = AsyncMock()

        asyncio.run(
            esios_get_indicator(
                123,
                start_date="2025-01-01T00:00:00Z",
                end_date="2025-01-01T01:00:00Z",
                ctx=ctx,
            )
        )

        self.assertEqual(ctx.info.await_count, 2)
        ctx.error.assert_not_awaited()
        self.assertIn("Calling the e·sios Indicator API get", ctx.info.await_args_list[0].args[0])

    @patch("esios_mcp.mcp.widgets.EsiosApiClient")
    def test_widget_tool_preserves_upstream_payload(self, client_class):
        client_class.return_value.get.return_value = WIDGET

        result = json.loads(asyncio.run(esios_get_widget("potencia")))

        self.assertEqual(result["data"], WIDGET)
        self.assertEqual(result["metadata"]["request"]["widget_id_or_slug"], "potencia")

    def test_invalid_date_range_fails_before_api_call(self):
        with self.assertRaisesRegex(ValueError, "on or before"):
            asyncio.run(
                esios_get_indicator(
                    123,
                    start_date="2025-01-02T00:00:00Z",
                    end_date="2025-01-01T00:00:00Z",
                )
            )

    def test_tools_are_registered(self):
        for name in (
            "esios_list_indicators",
            "esios_search_indicators",
            "esios_get_indicator",
            "esios_list_widgets",
            "esios_get_widget",
            "esios_list_archives",
            "esios_get_archive",
            "esios_get_archive_calculator_data",
            "esios_download_archive",
            "esios_list_json_archives",
            "esios_get_json_archive",
            "esios_download_json_archive",
            "esios_list_auctions",
            "esios_get_cached_widget_datetime",
            "esios_list_content",
            "esios_filter_news",
            "esios_get_content",
            "esios_get_content_by_id",
            "esios_get_offer_widget",
            "esios_get_offer_indicator",
            "esios_search_contents",
            "esios_search_contents_and_indicators",
        ):
            self.assertIsNotNone(asyncio.run(server.get_tool(name)), name)

    @patch("esios_mcp.mcp.indicators.EsiosApiClient")
    def test_missing_api_key_is_an_mcp_tool_error(self, client_class):
        from esios_mcp.api import EsiosApiError

        client_class.side_effect = EsiosApiError(
            "ESIOS_API_KEY is required",
            code="esios_missing_api_key",
        )

        result = asyncio.run(esios_list_indicators())

        self.assertIsInstance(result, ToolResult)
        self.assertTrue(result.is_error)
        content = result.content[0]
        self.assertIsInstance(content, TextContent)
        self.assertEqual(json.loads(content.text)["error"]["code"], "esios_missing_api_key")


if __name__ == "__main__":
    unittest.main()
