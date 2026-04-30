from __future__ import annotations

from datetime import date
from unittest import TestCase

from app.services.panchang import (
    calculate_karana,
    calculate_nakshatra,
    calculate_panchang_limbs,
    calculate_tithi,
    calculate_tithi_index,
    calculate_tithi_with_paksha,
    calculate_vara,
    calculate_yoga,
)


class PanchangCalculationTests(TestCase):
    def test_calculates_sample_limbs_from_phase1_longitudes(self) -> None:
        limbs = calculate_panchang_limbs(
            civil_date=date(2026, 5, 9),
            sun_longitude=24.181935403045713,
            moon_longitude=284.29321392321674,
        )

        self.assertEqual(limbs.tithi, "Saptami")
        self.assertEqual(limbs.vara, "Shanivara")
        self.assertEqual(limbs.nakshatra, "Shravana")
        self.assertEqual(limbs.yoga, "Shukla")
        self.assertEqual(limbs.karana, "Bava")

    def test_uses_modulo_for_wrapped_tithi_and_yoga(self) -> None:
        self.assertEqual(calculate_tithi(sun_longitude=350.0, moon_longitude=5.0), "Dwitiya")
        self.assertEqual(
            calculate_tithi_with_paksha(sun_longitude=350.0, moon_longitude=5.0),
            "Shukla Dwitiya",
        )
        self.assertEqual(calculate_tithi_index(sun_longitude=350.0, moon_longitude=5.0), 2)
        self.assertEqual(calculate_yoga(sun_longitude=300.0, moon_longitude=80.0), "Priti")

    def test_maps_nakshatra_boundaries(self) -> None:
        self.assertEqual(calculate_nakshatra(0.0), "Ashwini")
        self.assertEqual(calculate_nakshatra(359.999999), "Revati")

    def test_maps_karana_special_and_repeating_names(self) -> None:
        self.assertEqual(calculate_karana(sun_longitude=0.0, moon_longitude=0.0), "Kimstughna")
        self.assertEqual(calculate_karana(sun_longitude=0.0, moon_longitude=6.0), "Bava")
        self.assertEqual(calculate_karana(sun_longitude=0.0, moon_longitude=48.0), "Bava")
        self.assertEqual(calculate_karana(sun_longitude=0.0, moon_longitude=342.0), "Shakuni")
        self.assertEqual(calculate_karana(sun_longitude=0.0, moon_longitude=348.0), "Chatushpada")
        self.assertEqual(calculate_karana(sun_longitude=0.0, moon_longitude=354.0), "Naga")

    def test_maps_vara(self) -> None:
        self.assertEqual(calculate_vara(date(2026, 5, 3)), "Bhanuvara")
        self.assertEqual(calculate_vara(date(2026, 5, 9)), "Shanivara")