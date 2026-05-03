from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import swisseph as swe

from app.services.astronomy import AstronomyCalculationError, SwissEphemerisAstronomyService, _discover_ephemeris_path


class AstronomyServiceBackendTests(TestCase):
    def test_uses_explicit_ephemeris_path_when_provided(self) -> None:
        service = SwissEphemerisAstronomyService(ephemeris_path="/tmp/ephe")

        self.assertEqual(service.ephemeris_flag, swe.FLG_SWIEPH)
        self.assertEqual(service.ephemeris_path, "/tmp/ephe")

    def test_auto_discovers_ephemeris_path_from_se1_files(self) -> None:
        with TemporaryDirectory() as directory:
            Path(directory, "semo_18.se1").write_bytes(b"x")
            with patch("app.services.astronomy._PROJECT_ROOT", Path(directory)):
                discovered = _discover_ephemeris_path()
        self.assertEqual(discovered, directory)

    def test_raises_when_no_se1_files_found(self) -> None:
        with TemporaryDirectory() as empty_dir:
            with patch("app.services.astronomy._PROJECT_ROOT", Path(empty_dir)):
                with self.assertRaises(AstronomyCalculationError):
                    _discover_ephemeris_path()
