from __future__ import annotations

from unittest import TestCase
from unittest.mock import patch

import swisseph as swe

from app.services.astronomy import SwissEphemerisAstronomyService


class AstronomyServiceBackendTests(TestCase):
    def test_prefers_swiss_ephemeris_when_data_files_are_available(self) -> None:
        with patch(
            "app.services.astronomy.swe.calc_ut",
            return_value=((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), swe.FLG_SWIEPH),
        ):
            service = SwissEphemerisAstronomyService(ephemeris_path="/tmp/ephe")

        self.assertEqual(service.ephemeris_flag, swe.FLG_SWIEPH)
        self.assertEqual(service.ephemeris_backend, "swiss")

    def test_falls_back_to_moshier_when_swiss_files_are_unavailable(self) -> None:
        def calc_ut(_julian_day_ut: float, _body_id: int, requested_flag: int) -> tuple[tuple[float, ...], int]:
            ret_flag = swe.FLG_MOSEPH if requested_flag == swe.FLG_MOSEPH else swe.FLG_MOSEPH
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), ret_flag

        with patch("app.services.astronomy.swe.calc_ut", side_effect=calc_ut):
            service = SwissEphemerisAstronomyService()

        self.assertEqual(service.ephemeris_flag, swe.FLG_MOSEPH)
        self.assertEqual(service.ephemeris_backend, "moshier")
