from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from enum import Enum
from zoneinfo import ZoneInfo

import swisseph as swe


class AstronomyCalculationError(RuntimeError):
    pass


class CelestialBody(str, Enum):
    SUN = "sun"
    MOON = "moon"


@dataclass(frozen=True)
class SolarEvent:
    local_time: datetime
    utc_time: datetime
    julian_day_ut: float


@dataclass(frozen=True)
class BodyLongitude:
    tropical_longitude: float
    ayanamsa: float
    sidereal_longitude: float


@dataclass(frozen=True)
class Phase1AstronomyResult:
    local_midnight_jd_ut: float
    sunrise: SolarEvent
    sunset: SolarEvent
    sun: BodyLongitude
    moon: BodyLongitude
    ephemeris_path: str | None


@dataclass(frozen=True)
class SiderealLongitudes:
    sun: BodyLongitude
    moon: BodyLongitude


class SwissEphemerisAstronomyService:
    def __init__(
        self,
        ephemeris_path: str | None = None,
        atmospheric_pressure_mbar: float = 1013.25,
        temperature_celsius: float = 15.0,
    ) -> None:
        self.ephemeris_path = ephemeris_path or os.getenv("SWISSEPH_EPHE_PATH")
        self.atmospheric_pressure_mbar = atmospheric_pressure_mbar
        self.temperature_celsius = temperature_celsius
        self.ephemeris_flag = swe.FLG_SWIEPH

        if self.ephemeris_path:
            swe.set_ephe_path(self.ephemeris_path)

        swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)

    def calculate_phase1(
        self,
        civil_date: date,
        latitude: float,
        longitude: float,
        timezone_name: str,
    ) -> Phase1AstronomyResult:
        local_midnight_jd_ut = self.local_datetime_to_julian_day_ut(
            civil_date,
            time.min,
            timezone_name,
        )
        self._ensure_swiss_ephemeris_available(local_midnight_jd_ut)
        sunrise = self.calculate_sunrise(civil_date, latitude, longitude, timezone_name)
        sunset = self.calculate_sunset(civil_date, latitude, longitude, timezone_name)

        return Phase1AstronomyResult(
            local_midnight_jd_ut=local_midnight_jd_ut,
            sunrise=sunrise,
            sunset=sunset,
            sun=self.get_sidereal_longitude(CelestialBody.SUN, sunrise.julian_day_ut),
            moon=self.get_sidereal_longitude(CelestialBody.MOON, sunrise.julian_day_ut),
            ephemeris_path=self.ephemeris_path,
        )

    def get_sidereal_longitudes(self, julian_day_ut: float) -> SiderealLongitudes:
        return SiderealLongitudes(
            sun=self.get_sidereal_longitude(CelestialBody.SUN, julian_day_ut),
            moon=self.get_sidereal_longitude(CelestialBody.MOON, julian_day_ut),
        )

    def get_lunar_phase_angle(self, julian_day_ut: float) -> float:
        longitudes = self.get_sidereal_longitudes(julian_day_ut)
        return (longitudes.moon.sidereal_longitude - longitudes.sun.sidereal_longitude) % 360.0

    def find_previous_new_moon(self, julian_day_ut: float) -> float:
        self._ensure_swiss_ephemeris_available(julian_day_ut)

        newer_jd = julian_day_ut
        newer_angle = self.get_lunar_phase_angle(newer_jd)

        for _day in range(45):
            older_jd = newer_jd - 1.0
            older_angle = self.get_lunar_phase_angle(older_jd)

            if older_angle > newer_angle:
                return self._bisect_new_moon(older_jd, newer_jd)

            newer_jd = older_jd
            newer_angle = older_angle

        raise AstronomyCalculationError("Could not bracket the previous new moon within 45 days.")

    def find_next_new_moon(self, julian_day_ut: float) -> float:
        self._ensure_swiss_ephemeris_available(julian_day_ut)

        older_jd = julian_day_ut
        older_angle = self.get_lunar_phase_angle(older_jd)

        for _day in range(45):
            newer_jd = older_jd + 1.0
            newer_angle = self.get_lunar_phase_angle(newer_jd)

            if newer_angle < older_angle:
                return self._bisect_new_moon(older_jd, newer_jd)

            older_jd = newer_jd
            older_angle = newer_angle

        raise AstronomyCalculationError("Could not bracket the next new moon within 45 days.")

    def find_tithi_end(self, julian_day_ut: float) -> float:
        self._ensure_swiss_ephemeris_available(julian_day_ut)

        start_angle = self.get_lunar_phase_angle(julian_day_ut)
        current_tithi_index = int((start_angle % 360.0) // 12.0) + 1
        target_angle = (current_tithi_index * 12.0) % 360.0
        target_progress = (target_angle - start_angle) % 360.0

        if target_progress <= 1e-10:
            target_progress = 12.0

        lower_jd = julian_day_ut
        step_days = 0.25

        for _step in range(16):
            upper_jd = lower_jd + step_days
            upper_progress = self._lunar_phase_progress(julian_day_ut, start_angle, upper_jd)

            if upper_progress >= target_progress:
                return self._bisect_tithi_end(
                    lower_jd,
                    upper_jd,
                    julian_day_ut,
                    start_angle,
                    target_progress,
                )

            lower_jd = upper_jd

        raise AstronomyCalculationError("Could not bracket the Tithi end within 4 days.")

    def find_chaitra_new_moon(self, gregorian_year: int, timezone_name: str) -> float:
        search_jd = self.local_datetime_to_julian_day_ut(
            date(gregorian_year, 6, 1),
            time.min,
            timezone_name,
        )

        for _month in range(8):
            new_moon_jd = self.find_previous_new_moon(search_jd)
            sun = self.get_sidereal_longitude(CelestialBody.SUN, new_moon_jd)
            sun_rasi = int((sun.sidereal_longitude % 360.0) // 30.0)

            if sun_rasi == 11:
                return new_moon_jd

            search_jd = new_moon_jd - 1.0

        raise AstronomyCalculationError(
            f"Could not find Chaitra Shukla Pratipada anchor for {gregorian_year}."
        )

    @staticmethod
    def local_datetime_to_julian_day_ut(
        civil_date: date,
        local_time: time,
        timezone_name: str,
    ) -> float:
        local_moment = datetime.combine(civil_date, local_time, tzinfo=ZoneInfo(timezone_name))
        return SwissEphemerisAstronomyService.to_julian_day_ut(local_moment)

    @staticmethod
    def to_julian_day_ut(moment: datetime) -> float:
        if moment.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware before converting to Julian Day UT.")

        utc_moment = moment.astimezone(timezone.utc)
        decimal_hour = (
            utc_moment.hour
            + utc_moment.minute / 60.0
            + utc_moment.second / 3600.0
            + utc_moment.microsecond / 3_600_000_000.0
        )
        return swe.julday(
            utc_moment.year,
            utc_moment.month,
            utc_moment.day,
            decimal_hour,
            swe.GREG_CAL,
        )

    @staticmethod
    def from_julian_day_ut(julian_day_ut: float, timezone_name: str) -> tuple[datetime, datetime]:
        year, month, day, decimal_hour = swe.revjul(julian_day_ut, swe.GREG_CAL)
        utc_time = datetime(year, month, day, tzinfo=timezone.utc) + timedelta(hours=decimal_hour)
        local_time = utc_time.astimezone(ZoneInfo(timezone_name))
        return utc_time, local_time

    def calculate_sunrise(
        self,
        civil_date: date,
        latitude: float,
        longitude: float,
        timezone_name: str,
    ) -> SolarEvent:
        return self._calculate_solar_event(
            civil_date=civil_date,
            latitude=latitude,
            longitude=longitude,
            timezone_name=timezone_name,
            event_flag=swe.CALC_RISE,
        )

    def calculate_sunset(
        self,
        civil_date: date,
        latitude: float,
        longitude: float,
        timezone_name: str,
    ) -> SolarEvent:
        return self._calculate_solar_event(
            civil_date=civil_date,
            latitude=latitude,
            longitude=longitude,
            timezone_name=timezone_name,
            event_flag=swe.CALC_SET,
        )

    def get_sidereal_longitude(self, body: CelestialBody, julian_day_ut: float) -> BodyLongitude:
        body_id = {
            CelestialBody.SUN: swe.SUN,
            CelestialBody.MOON: swe.MOON,
        }[body]

        try:
            position, ret_flag = swe.calc_ut(julian_day_ut, body_id, self.ephemeris_flag)
            ayanamsa = swe.get_ayanamsa_ut(julian_day_ut)
        except swe.Error as exc:
            raise AstronomyCalculationError(str(exc)) from exc

        self._validate_swiss_ephemeris_flag(ret_flag)

        tropical_longitude = self._normalize_degrees(position[0])
        return BodyLongitude(
            tropical_longitude=tropical_longitude,
            ayanamsa=ayanamsa,
            sidereal_longitude=self._normalize_degrees(tropical_longitude - ayanamsa),
        )

    def _calculate_solar_event(
        self,
        civil_date: date,
        latitude: float,
        longitude: float,
        timezone_name: str,
        event_flag: int,
    ) -> SolarEvent:
        search_start_jd_ut = self.local_datetime_to_julian_day_ut(
            civil_date,
            time.min,
            timezone_name,
        )
        geopos = (longitude, latitude, 0.0)
        rsmi = event_flag | swe.BIT_DISC_CENTER

        try:
            result_code, event_times = swe.rise_trans(
                search_start_jd_ut,
                swe.SUN,
                rsmi,
                geopos,
                self.atmospheric_pressure_mbar,
                self.temperature_celsius,
                self.ephemeris_flag,
            )
        except swe.Error as exc:
            raise AstronomyCalculationError(str(exc)) from exc

        if result_code < 0:
            event_name = "sunrise" if event_flag == swe.CALC_RISE else "sunset"
            raise AstronomyCalculationError(
                f"Swiss Ephemeris could not calculate {event_name} for this date/location."
            )

        event_jd_ut = event_times[0]
        utc_time, local_time = self.from_julian_day_ut(event_jd_ut, timezone_name)
        return SolarEvent(local_time=local_time, utc_time=utc_time, julian_day_ut=event_jd_ut)

    def _ensure_swiss_ephemeris_available(self, julian_day_ut: float) -> None:
        for body_id in (swe.SUN, swe.MOON):
            try:
                _position, ret_flag = swe.calc_ut(julian_day_ut, body_id, self.ephemeris_flag)
            except swe.Error as exc:
                raise AstronomyCalculationError(str(exc)) from exc
            self._validate_swiss_ephemeris_flag(ret_flag)

    def _validate_swiss_ephemeris_flag(self, ret_flag: int) -> None:
        if ret_flag & swe.FLG_SWIEPH:
            return

        raise AstronomyCalculationError(
            "Swiss Ephemeris data files were not used. Set SWISSEPH_EPHE_PATH to a directory "
            "containing the required .se1 files, for example sepl_18.se1 and semo_18.se1 for 1800-2399."
        )

    def _bisect_new_moon(self, older_jd: float, newer_jd: float) -> float:
        lower_jd = older_jd
        upper_jd = newer_jd

        for _iteration in range(60):
            midpoint_jd = (lower_jd + upper_jd) / 2.0
            midpoint_phase = self._signed_new_moon_phase(midpoint_jd)

            if midpoint_phase >= 0.0:
                upper_jd = midpoint_jd
            else:
                lower_jd = midpoint_jd

        return (lower_jd + upper_jd) / 2.0

    def _signed_new_moon_phase(self, julian_day_ut: float) -> float:
        phase_angle = self.get_lunar_phase_angle(julian_day_ut)
        if phase_angle > 180.0:
            return phase_angle - 360.0
        return phase_angle

    def _bisect_tithi_end(
        self,
        lower_jd: float,
        upper_jd: float,
        start_jd: float,
        start_angle: float,
        target_progress: float,
    ) -> float:
        for _iteration in range(48):
            midpoint_jd = (lower_jd + upper_jd) / 2.0
            midpoint_progress = self._lunar_phase_progress(start_jd, start_angle, midpoint_jd)

            if midpoint_progress >= target_progress:
                upper_jd = midpoint_jd
            else:
                lower_jd = midpoint_jd

        return (lower_jd + upper_jd) / 2.0

    def _lunar_phase_progress(self, start_jd: float, start_angle: float, julian_day_ut: float) -> float:
        if julian_day_ut < start_jd:
            raise ValueError("Lunar phase progress can only be measured forward in time.")

        current_angle = self.get_lunar_phase_angle(julian_day_ut)
        return (current_angle - start_angle) % 360.0

    @staticmethod
    def _normalize_degrees(value: float) -> float:
        return value % 360.0
