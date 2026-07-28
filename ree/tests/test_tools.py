import json
import unittest
from unittest.mock import patch

from ree_mcp.tools.data import ree_data
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
    @patch("ree_mcp.tools._common.requests.get")
    def test_ree_data_calls_api_and_preserves_payload(self, get):
        get.return_value = Response(DATA_PAYLOAD)

        result = json.loads(
            ree_data(
                "demanda",
                "evolucion",
                "2024-01-01T00:00",
                "2024-01-01T23:59",
            )
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
            ree_data(
                "demanda",
                "evolucion",
                "2024-01-01T00:00",
                "2024-01-01T23:59",
                geo_limit="peninsular",
            )

    def test_rejects_ccaa_as_geo_trunc(self):
        with self.assertRaisesRegex(ValueError, "geo_trunc must be one of: electric_system"):
            ree_data(
                "demanda",
                "evolucion",
                "2024-01-01T00:00",
                "2024-01-01T23:59",
                geo_trunc="ccaa",
                geo_limit="ccaa",
                geo_ids="1",
            )

    @patch("ree_mcp.tools._common.requests.get")
    def test_builds_official_regional_query(self, get):
        get.return_value = Response(DATA_PAYLOAD)

        ree_data(
            "demanda",
            "evolucion",
            "2024-01-01T00:00",
            "2024-01-01T23:59",
            geo_trunc="electric_system",
            geo_limit="ccaa",
            geo_ids="1",
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

    @patch("ree_mcp.tools._common.requests.get")
    def test_rejects_regional_real_time_query_before_api_call(self, get):
        with self.assertRaisesRegex(ValueError, "national real-time curve"):
            ree_data(
                "demanda",
                "demanda-tiempo-real",
                "2024-01-01T00:00",
                "2024-01-01T23:59",
                geo_trunc="electric_system",
                geo_limit="ccaa",
                geo_ids="1",
            )

        get.assert_not_called()


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
