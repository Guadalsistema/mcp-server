import asyncio
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastmcp.tools import ToolResult
from fastmcp.exceptions import ToolError, ValidationError

from esios.app import server as esios_server
from glossary.app import server as glossary_server
from glossary.models import (
    GlossaryCatalog,
    GlossaryEntry,
    GlossarySearchResponse,
    GlossarySource,
)
from glossary.service import DEFAULT_GLOSSARY_SERVICE
from ree.app import server as ree_server


RETRIEVED_AT = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
ARGUMENTS = {
    "request": {
        "query": "cable",
        "lookup_forms": ["cable"],
        "language": "es",
        "limit": 10,
    }
}


def source_catalog(source: GlossarySource) -> GlossaryCatalog:
    is_ree = source == "ree"
    return GlossaryCatalog(
        source=source,
        language="es",
        entries=[
            GlossaryEntry(
                source=source,
                source_name="REE glossary" if is_ree else "e·sios glossary",
                source_id=None if is_ree else "886",
                canonical_label="Cable",
                definition="Conductor eléctrico.",
                language="es",
                domain="electrical" if is_ree else None,
            )
        ],
        retrieved_at=RETRIEVED_AT,
    )


class GlossaryMcpContractTests(unittest.TestCase):
    def setUp(self):
        DEFAULT_GLOSSARY_SERVICE.clear_cache()

    def test_source_and_combined_tools_advertise_the_structured_output_schema(self):
        for server, name in (
            (ree_server, "ree_glossary_search"),
            (esios_server, "esios_glossary_search"),
            (glossary_server, "glossary_search"),
        ):
            tool = asyncio.run(server.get_tool(name))
            assert tool is not None
            schema = tool.output_schema
            assert schema is not None
            self.assertEqual(schema["properties"]["schema_version"]["const"], "1")
            self.assertIn("candidates", schema["properties"])
            self.assertTrue(
                {"schema_version", "candidates"}.issubset(schema["required"])
            )
            candidate_schema = schema["$defs"]["GlossaryCandidate"]
            self.assertIn("aliases", candidate_schema["required"])
            self.assertNotIn("x-fastmcp-wrap-result", schema)

    def test_whitespace_only_lookup_is_rejected_by_the_input_contract(self):
        invalid_arguments = {
            "request": {
                "query": " ",
                "lookup_forms": ["cable"],
                "language": "es",
            }
        }

        with self.assertRaises(ValidationError):
            asyncio.run(
                ree_server.call_tool("ree_glossary_search", invalid_arguments)
            )

    @patch("ree.api.glossary.load_glossary", return_value=source_catalog("ree"))
    def test_ree_tool_returns_structured_content(self, load):
        result = asyncio.run(ree_server.call_tool("ree_glossary_search", ARGUMENTS))

        self.assertIsInstance(result, ToolResult)
        response = GlossarySearchResponse.model_validate_json(
            json.dumps(result.structured_content)
        )
        self.assertEqual(response.candidates[0].source, "REE glossary")
        load.assert_called_once_with("es")

    @patch("esios.api.glossary.load_glossary", return_value=source_catalog("esios"))
    def test_esios_tool_returns_structured_content(self, load):
        result = asyncio.run(esios_server.call_tool("esios_glossary_search", ARGUMENTS))

        response = GlossarySearchResponse.model_validate_json(
            json.dumps(result.structured_content)
        )
        self.assertEqual(response.candidates[0].id, "esios:es:886")
        load.assert_called_once_with("es")

    @patch("esios.api.glossary.load_glossary", return_value=source_catalog("esios"))
    @patch("ree.api.glossary.load_glossary", return_value=source_catalog("ree"))
    def test_combined_tool_returns_candidates_from_both_sources(self, ree_load, esios_load):
        result = asyncio.run(glossary_server.call_tool("glossary_search", ARGUMENTS))

        response = GlossarySearchResponse.model_validate_json(
            json.dumps(result.structured_content)
        )
        self.assertEqual(
            {candidate.source for candidate in response.candidates},
            {"REE glossary", "e·sios glossary"},
        )
        ree_load.assert_called_once_with("es")
        esios_load.assert_called_once_with("es")

    @patch("ree.api.glossary.load_glossary", side_effect=RuntimeError("upstream failed"))
    def test_upstream_failure_is_an_mcp_tool_error(self, load):
        with self.assertRaisesRegex(ToolError, "ree_glossary_search"):
            asyncio.run(ree_server.call_tool("ree_glossary_search", ARGUMENTS))

        load.assert_called_once_with("es")

    @patch("esios.api.glossary.load_glossary", return_value=source_catalog("esios"))
    @patch("ree.api.glossary.load_glossary", side_effect=RuntimeError("upstream failed"))
    def test_combined_tool_does_not_return_partial_results(self, ree_load, esios_load):
        with self.assertRaisesRegex(ToolError, "glossary_search"):
            asyncio.run(glossary_server.call_tool("glossary_search", ARGUMENTS))

        ree_load.assert_called_once_with("es")
        esios_load.assert_called_once_with("es")

    def test_combined_server_registers_only_glossary_tools(self):
        names = {tool.name for tool in asyncio.run(glossary_server.list_tools())}

        self.assertEqual(
            names,
            {"glossary_search", "ree_glossary_search", "esios_glossary_search"},
        )


if __name__ == "__main__":
    unittest.main()
