import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from ree.api.glossary import glossary_records_to_catalog, load_glossary


class ReeGlossaryApiTests(unittest.TestCase):
    def test_bridge_preserves_the_ree_domain(self):
        retrieved_at = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

        result = glossary_records_to_catalog(
            [
                {
                    "category": "environmental",
                    "letter": "C",
                    "term": "Campo eléctrico",
                    "definition": "Descripción ambiental.",
                }
            ],
            "es",
            retrieved_at=retrieved_at,
        )

        self.assertEqual(result.source, "ree")
        self.assertEqual(result.retrieved_at, retrieved_at)
        self.assertEqual(result.entries[0].domain, "environmental")
        self.assertEqual(result.entries[0].aliases, [])

    @patch("ree.api.glossary._fetch_glossary", return_value="<html></html>")
    def test_empty_upstream_document_is_a_parsing_failure(self, fetch):
        with self.assertRaisesRegex(RuntimeError, "did not contain"):
            load_glossary("es")

        fetch.assert_called_once_with("es")


if __name__ == "__main__":
    unittest.main()
