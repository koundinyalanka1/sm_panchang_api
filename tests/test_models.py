from __future__ import annotations

from unittest import TestCase

from app.models import PanchangLimbsResponse


class ModelContractTests(TestCase):
    def test_panchang_limbs_response_includes_end_times_and_next_values(self) -> None:
        response = PanchangLimbsResponse(
            tithi="Krishna Saptami",
            tithi_end_time="02:03 PM",
            next_tithi="Krishna Ashtami",
            vara="Shanivara",
            nakshatra="Shravana",
            nakshatra_end_time="09:22 AM",
            next_nakshatra="Dhanishta",
            yoga="Shukla",
            yoga_end_time="11:40 AM",
            next_yoga="Brahma",
            karana="Bava",
            karana_end_time="02:03 PM",
            next_karana="Balava",
        )

        self.assertEqual(response.next_tithi, "Krishna Ashtami")
        self.assertEqual(response.nakshatra_end_time, "09:22 AM")
        self.assertEqual(response.next_nakshatra, "Dhanishta")
        self.assertEqual(response.yoga_end_time, "11:40 AM")
        self.assertEqual(response.next_yoga, "Brahma")
        self.assertEqual(response.karana_end_time, "02:03 PM")
        self.assertEqual(response.next_karana, "Balava")
