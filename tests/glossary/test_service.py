import asyncio
import time
import unittest
from datetime import datetime, timezone

from glossary.models import (
    GlossaryCatalog,
    GlossaryDomain,
    GlossaryEntry,
    GlossaryLanguage,
    GlossarySearchRequest,
    GlossarySource,
)
from glossary.service import GlossaryService, glossary_version, search_entries


RETRIEVED_AT = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def entry(
    label: str,
    definition: str,
    *,
    source: GlossarySource = "ree",
    source_id: str | None = None,
    language: GlossaryLanguage = "es",
    domain: GlossaryDomain | None = "electrical",
    aliases: list[str] | None = None,
) -> GlossaryEntry:
    return GlossaryEntry(
        source=source,
        source_name="REE glossary" if source == "ree" else "e·sios glossary",
        source_id=source_id,
        canonical_label=label,
        definition=definition,
        language=language,
        domain=domain,
        aliases=aliases or [],
    )


def catalog(
    source: GlossarySource,
    entries: list[GlossaryEntry],
    *,
    language: GlossaryLanguage = "es",
    retrieved_at: datetime = RETRIEVED_AT,
) -> GlossaryCatalog:
    return GlossaryCatalog(
        source=source,
        language=language,
        entries=entries,
        retrieved_at=retrieved_at,
    )


def request(
    *forms: str,
    query: str = "sin coincidencia",
    language: GlossaryLanguage = "es",
    domain: GlossaryDomain | None = None,
    limit: int = 10,
) -> GlossarySearchRequest:
    return GlossarySearchRequest(
        query=query,
        lookup_forms=list(forms),
        language=language,
        domain=domain,
        limit=limit,
    )


class MatchingTests(unittest.TestCase):
    def test_all_lookup_forms_are_normalized_classified_and_ranked(self):
        entries = [
            entry("Balance", "Mecanismo para mantener el equilibrio del sistema."),
            entry("Mercado diario", "Mercado de energía para el día siguiente."),
            entry(
                "Reserva de regulación",
                "Capacidad disponible para regulación.",
                aliases=["reserva"],
            ),
            entry("Energía", "Capacidad para realizar trabajo."),
        ]

        result = search_entries(
            entries,
            request("ENERGIA", "reserva", "mercado", "equilíbrio"),
        )

        self.assertEqual(
            [(candidate.canonical_label, candidate.match_type, candidate.score) for candidate in result],
            [
                ("Energía", "exact", 1.0),
                ("Reserva de regulación", "alias", 0.9),
                ("Mercado diario", "prefix", 0.7),
                ("Balance", "definition", 0.5),
            ],
        )

    def test_query_itself_participates_in_matching(self):
        result = search_entries(
            [entry("Energía", "Capacidad para realizar trabajo.")],
            request("otra-forma", query="energia"),
        )

        self.assertEqual(result[0].match_type, "exact")

    def test_domain_language_deduplication_and_limit_are_applied(self):
        entries = [
            entry("Reserva", "Definición A", domain="electrical"),
            entry("Reserva", "Definición A", domain="electrical"),
            entry("Reserva", "Definición ambiental", domain="environmental"),
            entry("Reserva secundaria", "Otra definición", domain="electrical"),
            entry("Reserva", "English definition", language="en", domain="electrical"),
        ]

        result = search_entries(
            entries,
            request("reserva", domain="electrical", limit=1),
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].canonical_label, "Reserva")
        self.assertEqual(result[0].id, "ree:es:electrical:reserva")

    def test_ree_homonyms_are_preserved_with_deterministic_ids(self):
        first = entry("Reserva", "Definición Z")
        second = entry("Reserva", "Definición A")
        search_request = request("reserva")

        forward = search_entries([first, second], search_request)
        reverse = search_entries([second, first], search_request)

        self.assertEqual(forward, reverse)
        self.assertEqual(len(forward), 2)
        self.assertEqual(
            {candidate.definition for candidate in forward},
            {"Definición A", "Definición Z"},
        )
        self.assertTrue(
            all(":meaning-" in candidate.id for candidate in forward)
        )

    def test_no_match_returns_an_empty_list(self):
        self.assertEqual(
            search_entries([entry("Energía", "Definición")], request("potencia")),
            [],
        )

    def test_upstream_ids_are_used_for_stable_esios_candidate_ids(self):
        entries = [
            entry(
                "Cable",
                "Conductor eléctrico.",
                source="esios",
                source_id="886",
                domain=None,
            )
        ]

        first = search_entries(entries, request("cable"))[0]
        second = search_entries(entries, request("CABLE"))[0]

        self.assertEqual(first.id, "esios:es:886")
        self.assertEqual(first.id, second.id)

    def test_version_is_content_based_and_order_independent(self):
        first = entry("Energía", "Primera definición")
        second = entry("Reserva", "Segunda definición")

        self.assertEqual(
            glossary_version([first, second]),
            glossary_version([second, first]),
        )
        self.assertNotEqual(
            glossary_version([first, second]),
            glossary_version([first, entry("Reserva", "Definición modificada")]),
        )

    def test_version_is_order_independent_for_same_label_homonyms(self):
        first = entry("Reserva", "Primera definición")
        second = entry("Reserva", "Segunda definición")

        self.assertEqual(
            glossary_version([first, second]),
            glossary_version([second, first]),
        )


class CacheTests(unittest.TestCase):
    def test_cache_ttl_must_be_positive_and_finite(self):
        for ttl in (0, -1, float("inf"), float("nan")):
            with self.subTest(ttl=ttl):
                with self.assertRaisesRegex(ValueError, "finite"):
                    GlossaryService({}, ttl_seconds=ttl)

    def test_repeated_searches_reuse_the_catalog(self):
        calls = []

        def loader(language):
            calls.append(language)
            return catalog("ree", [entry("Energía", "Definición")])

        service = GlossaryService({"ree": loader})
        search_request = request("energia")

        first = asyncio.run(service.search(("ree",), search_request))
        second = asyncio.run(service.search(("ree",), search_request))

        self.assertEqual(calls, ["es"])
        self.assertEqual(first.glossary_version, second.glossary_version)
        self.assertEqual(first.retrieved_at, RETRIEVED_AT)

    def test_languages_use_separate_cache_entries(self):
        calls = []

        def loader(language):
            calls.append(language)
            return catalog(
                "ree",
                [
                    entry(
                        "Energía" if language == "es" else "Energy",
                        "Definición" if language == "es" else "Definition",
                        language=language,
                    )
                ],
                language=language,
            )

        service = GlossaryService({"ree": loader})

        asyncio.run(service.search(("ree",), request("energia")))
        asyncio.run(
            service.search(
                ("ree",),
                request("energy", language="en"),
            )
        )

        self.assertEqual(calls, ["es", "en"])

    def test_concurrent_searches_share_one_refresh(self):
        calls = []

        def loader(language):
            calls.append(language)
            time.sleep(0.05)
            return catalog("ree", [entry("Energía", "Definición")])

        service = GlossaryService({"ree": loader})
        search_request = request("energia")

        async def search_twice():
            return await asyncio.gather(
                service.search(("ree",), search_request),
                service.search(("ree",), search_request),
            )

        asyncio.run(search_twice())

        self.assertEqual(calls, ["es"])

    def test_refresh_lock_is_recreated_for_a_new_event_loop(self):
        now = [0.0]
        calls = []

        def loader(language):
            calls.append(language)
            time.sleep(0.02)
            return catalog("ree", [entry("Energía", "Definición")])

        service = GlossaryService(
            {"ree": loader},
            ttl_seconds=1,
            clock=lambda: now[0],
        )
        search_request = request("energia")

        async def concurrent_search():
            return await asyncio.gather(
                service.search(("ree",), search_request),
                service.search(("ree",), search_request),
            )

        asyncio.run(concurrent_search())
        now[0] = 2.0
        asyncio.run(concurrent_search())

        self.assertEqual(calls, ["es", "es"])

    def test_failed_refresh_does_not_return_stale_data(self):
        now = [0.0]
        calls = 0

        def loader(language):
            nonlocal calls
            calls += 1
            if calls > 1:
                raise RuntimeError("upstream unavailable")
            return catalog("ree", [entry("Energía", "Definición")])

        service = GlossaryService(
            {"ree": loader},
            ttl_seconds=1,
            clock=lambda: now[0],
        )
        asyncio.run(service.search(("ree",), request("energia")))
        now[0] = 2.0

        with self.assertRaisesRegex(RuntimeError, "upstream unavailable"):
            asyncio.run(service.search(("ree",), request("energia")))

    def test_combined_search_preserves_source_provenance(self):
        service = GlossaryService(
            {
                "ree": lambda language: catalog(
                    "ree", [entry("Cable", "Definición REE")]
                ),
                "esios": lambda language: catalog(
                    "esios",
                    [
                        entry(
                            "Cable",
                            "Definición e·sios",
                            source="esios",
                            source_id="886",
                            domain=None,
                        )
                    ],
                ),
            }
        )

        result = asyncio.run(service.search(("ree", "esios"), request("cable")))

        self.assertEqual(
            [candidate.source for candidate in result.candidates],
            ["e·sios glossary", "REE glossary"],
        )

    def test_domain_filtered_search_keeps_domainless_esios_entries(self):
        service = GlossaryService(
            {
                "ree": lambda language: catalog("ree", [entry("Cable", "Definición REE")]),
                "esios": lambda language: catalog(
                    "esios",
                    [
                        entry(
                            "Cable",
                            "Definición e·sios",
                            source="esios",
                            source_id="886",
                            domain=None,
                        )
                    ],
                ),
            }
        )

        result = asyncio.run(
            service.search(("ree", "esios"), request("cable", domain="electrical"))
        )

        self.assertEqual(
            [candidate.source for candidate in result.candidates],
            ["e·sios glossary", "REE glossary"],
        )

    def test_combined_retrieval_time_uses_the_oldest_source_fetch(self):
        older = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
        newer = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
        service = GlossaryService(
            {
                "ree": lambda language: catalog(
                    "ree",
                    [entry("Cable", "Definición REE")],
                    retrieved_at=older,
                ),
                "esios": lambda language: catalog(
                    "esios",
                    [
                        entry(
                            "Cable",
                            "Definición e·sios",
                            source="esios",
                            source_id="886",
                            domain=None,
                        )
                    ],
                    retrieved_at=newer,
                ),
            }
        )

        result = asyncio.run(service.search(("ree", "esios"), request("cable")))

        self.assertEqual(result.retrieved_at, older)


if __name__ == "__main__":
    unittest.main()
