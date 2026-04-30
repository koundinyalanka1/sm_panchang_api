from __future__ import annotations

from datetime import date, datetime
from unittest import TestCase

from app.main import _format_clock_time


class MainFormattingTests(TestCase):
    def test_formats_same_day_clock_time_without_suffix(self) -> None:
        self.assertEqual(
            _format_clock_time(datetime(2026, 5, 9, 14, 3, 12), date(2026, 5, 9)),
            "02:03 PM",
        )

    def test_formats_next_day_clock_time_with_suffix(self) -> None:
        self.assertEqual(
            _format_clock_time(datetime(2026, 5, 10, 2, 35, 12), date(2026, 5, 9)),
            "02:35 AM (Next Day)",
        )

    def test_marks_next_day_when_rounding_crosses_midnight(self) -> None:
        self.assertEqual(
            _format_clock_time(datetime(2026, 5, 9, 23, 59, 45), date(2026, 5, 9)),
            "12:00 AM (Next Day)",
        )
