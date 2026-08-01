import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from esios.api import EsiosApiError
from esios.api.glossary import glossary_payload_to_catalog, load_glossary


GLOSSARY_PAYLOAD = {
    "contents": [
        {
            "id": 886,
            "title": "Cable",
            "slug": "cable",
            "body": "<p>Conductor <strong>eléctrico</strong>.</p><script>ignore()</script>",
            "type": "glossaries",
            "taxonomy_terms": [],
            "vocabularies": [],
        }
    ],
    "meta": {"size": 1},
}


class EsiosGlossaryApiTests(unittest.TestCase):
    def test_bridge_preserves_upstream_identity_and_cleans_definition_html(self):
        retrieved_at = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

        result = glossary_payload_to_catalog(
            GLOSSARY_PAYLOAD,
            "es",
            retrieved_at=retrieved_at,
        )

        self.assertEqual(result.source, "esios")
        self.assertEqual(result.retrieved_at, retrieved_at)
        self.assertEqual(result.entries[0].source_id, "886")
        self.assertEqual(result.entries[0].canonical_label, "Cable")
        self.assertEqual(result.entries[0].definition, "Conductor eléctrico.")
        self.assertIsNone(result.entries[0].domain)
        self.assertEqual(result.entries[0].aliases, [])

    @patch("esios.api.glossary.EsiosApiClient")
    def test_loader_uses_the_localized_glossaries_endpoint(self, client_class):
        client = client_class.return_value
        client.get.return_value = GLOSSARY_PAYLOAD

        result = load_glossary("en", api_key="direct-key")

        self.assertEqual(result.language, "en")
        client_class.assert_called_once_with(api_key="direct-key")
        client.get.assert_called_once_with(
            "/en/glossaries",
            params={"locale": "en"},
        )

    def test_invalid_upstream_shape_fails_instead_of_returning_no_matches(self):
        with self.assertRaises(EsiosApiError) as raised:
            glossary_payload_to_catalog({"unexpected": []}, "es")

        self.assertEqual(raised.exception.code, "esios_invalid_response")


if __name__ == "__main__":
    unittest.main()
