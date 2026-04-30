from __future__ import annotations

from datetime import date
from unittest import TestCase

from app.services.calendrical import (
    calculate_ayana,
    calculate_calendrical_elements,
    calculate_is_adhika_masa,
    calculate_masa,
    calculate_paksha,
    calculate_rasi,
    calculate_rutuvu,
    calculate_samvatsara,
)


class CalendricalCalculationTests(TestCase):
    def test_calculates_sample_calendrical_elements(self) -> None:
        elements = calculate_calendrical_elements(
            civil_date=date(2026, 5, 9),
            sunrise_jd_ut=2461169.512180298,
            sun_longitude=24.181935403045713,
            tithi_index=22,
            new_moon_sun_longitude=3.0,
            next_new_moon_sun_longitude=34.0,
            chaitra_new_moon_jd_ut=2461120.0,
            month_convention="AMANTA",
        )

        self.assertEqual(elements.samvatsara, "Parabhava")
        self.assertEqual(elements.masa, "Vaisakha")
        self.assertFalse(elements.is_adhika_masa)
        self.assertEqual(elements.paksha, "Krishna")
        self.assertEqual(elements.rutuvu, "Vasanta")
        self.assertEqual(elements.ayana, "Uttarayana")

    def test_calculates_paksha_from_tithi_index(self) -> None:
        self.assertEqual(calculate_paksha(1), "Shukla")
        self.assertEqual(calculate_paksha(15), "Shukla")
        self.assertEqual(calculate_paksha(16), "Krishna")
        self.assertEqual(calculate_paksha(30), "Krishna")

    def test_calculates_ayana_boundaries(self) -> None:
        self.assertEqual(calculate_ayana(270.0), "Uttarayana")
        self.assertEqual(calculate_ayana(89.999), "Uttarayana")
        self.assertEqual(calculate_ayana(90.0), "Dakshinayana")
        self.assertEqual(calculate_ayana(269.999), "Dakshinayana")

    def test_calculates_rutuvu_from_rasi(self) -> None:
        self.assertEqual(calculate_rasi(359.0), 11)
        self.assertEqual(calculate_rutuvu(359.0), "Vasanta")
        self.assertEqual(calculate_rutuvu(30.0), "Grishma")
        self.assertEqual(calculate_rutuvu(150.0), "Sharad")
        self.assertEqual(calculate_rutuvu(300.0), "Shishira")

    def test_calculates_masa_for_amanta_and_purnimanta_shift(self) -> None:
        self.assertEqual(calculate_masa(355.0, "Shukla", "AMANTA"), "Chaitra")
        self.assertEqual(calculate_masa(355.0, "Krishna", "AMANTA"), "Chaitra")
        self.assertEqual(calculate_masa(355.0, "Krishna", "PURNIMANTA"), "Vaisakha")
        self.assertEqual(calculate_masa(5.0, "Krishna", "PURNIMANTA"), "Jyeshtha")

    def test_calculates_purnimanta_krishna_masa_from_next_lunation(self) -> None:
        elements = calculate_calendrical_elements(
            civil_date=date(2026, 5, 9),
            sunrise_jd_ut=2461169.512180298,
            sun_longitude=24.181935403045713,
            tithi_index=22,
            new_moon_sun_longitude=3.0,
            next_new_moon_sun_longitude=34.0,
            following_new_moon_sun_longitude=65.0,
            chaitra_new_moon_jd_ut=2461120.0,
            month_convention="PURNIMANTA",
        )

        self.assertEqual(elements.masa, "Jyeshtha")
        self.assertFalse(elements.is_adhika_masa)
        self.assertEqual(elements.paksha, "Krishna")

    def test_calculates_purnimanta_krishna_adhika_status_from_next_lunation(self) -> None:
        elements_before_adhika_new_moon = calculate_calendrical_elements(
            civil_date=date(2026, 5, 9),
            sunrise_jd_ut=2461169.512180298,
            sun_longitude=24.181935403045713,
            tithi_index=22,
            new_moon_sun_longitude=3.0,
            next_new_moon_sun_longitude=34.0,
            following_new_moon_sun_longitude=59.0,
            chaitra_new_moon_jd_ut=2461120.0,
            month_convention="PURNIMANTA",
        )
        elements_before_regular_new_moon = calculate_calendrical_elements(
            civil_date=date(2026, 6, 9),
            sunrise_jd_ut=2461200.512180298,
            sun_longitude=54.18193540304571,
            tithi_index=22,
            new_moon_sun_longitude=34.0,
            next_new_moon_sun_longitude=59.0,
            following_new_moon_sun_longitude=91.0,
            chaitra_new_moon_jd_ut=2461120.0,
            month_convention="PURNIMANTA",
        )

        self.assertEqual(elements_before_adhika_new_moon.masa, "Adhika Jyeshtha")
        self.assertTrue(elements_before_adhika_new_moon.is_adhika_masa)
        self.assertEqual(elements_before_regular_new_moon.masa, "Jyeshtha")
        self.assertFalse(elements_before_regular_new_moon.is_adhika_masa)

    def test_calculates_adhika_masa_flag_and_prefix(self) -> None:
        self.assertTrue(calculate_is_adhika_masa(45.0, 59.0))
        self.assertFalse(calculate_is_adhika_masa(45.0, 61.0))
        self.assertEqual(calculate_masa(45.0, "Shukla", "AMANTA", True), "Adhika Jyeshtha")

    def test_calculates_samvatsara_around_chaitra_anchor(self) -> None:
        chaitra_anchor_jd = 2461120.0
        self.assertEqual(
            calculate_samvatsara(date(2026, 3, 1), 2461100.0, chaitra_anchor_jd),
            "Vishvavasu",
        )
        self.assertEqual(
            calculate_samvatsara(date(2026, 5, 9), 2461169.512180298, chaitra_anchor_jd),
            "Parabhava",
        )