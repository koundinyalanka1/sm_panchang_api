from __future__ import annotations

from unittest import TestCase

from app.services.festivals import identify_festivals


class FestivalIdentificationTests(TestCase):
    def test_identifies_single_and_multiple_festivals(self) -> None:
        self.assertEqual(
            identify_festivals("Chaitra", "Shukla", "Pratipada"),
            ["Ugadi", "Gudi Padwa"],
        )
        self.assertEqual(
            identify_festivals("Ashvina", "Shukla", "Dashami"),
            ["Vijaya Dashami", "Dussehra"],
        )
        self.assertEqual(
            identify_festivals("Phalguna", "Shukla", "Purnima"),
            ["Holi"],
        )

    def test_returns_empty_list_when_no_festival_matches(self) -> None:
        self.assertEqual(identify_festivals("Vaisakha", "Krishna", "Saptami"), [])

    def test_uses_purnimanta_krishna_paksha_festival_months(self) -> None:
        self.assertEqual(
            identify_festivals(
                "Bhadrapada",
                "Krishna",
                "Ashtami",
                month_convention="PURNIMANTA",
            ),
            ["Krishna Janmashtami"],
        )
        self.assertEqual(
            identify_festivals(
                "Phalguna",
                "Krishna",
                "Chaturdashi",
                month_convention="PURNIMANTA",
            ),
            ["Maha Shivaratri"],
        )
        self.assertEqual(
            identify_festivals(
                "Shravana",
                "Krishna",
                "Ashtami",
                month_convention="PURNIMANTA",
            ),
            [],
        )

    def test_preserves_amanta_krishna_paksha_festival_months(self) -> None:
        self.assertEqual(
            identify_festivals("Shravana", "Krishna", "Ashtami"),
            ["Krishna Janmashtami"],
        )
        self.assertEqual(
            identify_festivals("Magha", "Krishna", "Chaturdashi"),
            ["Maha Shivaratri"],
        )
        self.assertEqual(
            identify_festivals("Bhadrapada", "Krishna", "Ashtami"),
            [],
        )

    def test_suppresses_festivals_during_adhika_masa(self) -> None:
        self.assertEqual(
            identify_festivals("Ashvina", "Shukla", "Dashami", is_adhika_masa=True),
            [],
        )