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

    def test_suppresses_festivals_during_adhika_masa(self) -> None:
        self.assertEqual(
            identify_festivals("Ashvina", "Shukla", "Dashami", is_adhika_masa=True),
            [],
        )