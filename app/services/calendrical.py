from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from enum import Enum


MASA_SEQUENCE = [
    "Chaitra",
    "Vaisakha",
    "Jyeshtha",
    "Ashadha",
    "Shravana",
    "Bhadrapada",
    "Ashvina",
    "Kartika",
    "Margashirsha",
    "Pausha",
    "Magha",
    "Phalguna",
]

MASA_BY_NEW_MOON_SUN_RASI = {
    11: "Chaitra",
    0: "Vaisakha",
    1: "Jyeshtha",
    2: "Ashadha",
    3: "Shravana",
    4: "Bhadrapada",
    5: "Ashvina",
    6: "Kartika",
    7: "Margashirsha",
    8: "Pausha",
    9: "Magha",
    10: "Phalguna",
}

RUTUVU_BY_RASI = {
    11: "Vasanta",
    0: "Vasanta",
    1: "Grishma",
    2: "Grishma",
    3: "Varsha",
    4: "Varsha",
    5: "Sharad",
    6: "Sharad",
    7: "Hemanta",
    8: "Hemanta",
    9: "Shishira",
    10: "Shishira",
}

SAMVATSARA_NAMES = [
    "Prabhava",
    "Vibhava",
    "Shukla",
    "Pramoda",
    "Prajapati",
    "Angirasa",
    "Shrimukha",
    "Bhava",
    "Yuva",
    "Dhatri",
    "Ishvara",
    "Bahudhanya",
    "Pramathi",
    "Vikrama",
    "Vrisha",
    "Chitrabhanu",
    "Subhanu",
    "Tarana",
    "Parthiva",
    "Vyaya",
    "Sarvajit",
    "Sarvadhari",
    "Virodhi",
    "Vikriti",
    "Khara",
    "Nandana",
    "Vijaya",
    "Jaya",
    "Manmatha",
    "Durmukhi",
    "Hemalambi",
    "Vilambi",
    "Vikari",
    "Sharvari",
    "Plava",
    "Shubhakrit",
    "Shobhakrit",
    "Krodhi",
    "Vishvavasu",
    "Parabhava",
    "Plavanga",
    "Kilaka",
    "Saumya",
    "Sadharana",
    "Virodhikrit",
    "Paridhavi",
    "Pramadicha",
    "Ananda",
    "Rakshasa",
    "Nala",
    "Pingala",
    "Kalayukti",
    "Siddharthi",
    "Raudra",
    "Durmati",
    "Dundubhi",
    "Rudhirodgari",
    "Raktaksha",
    "Krodhana",
    "Akshaya",
]


@dataclass(frozen=True)
class CalendricalElements:
    samvatsara: str
    masa: str
    is_adhika_masa: bool
    paksha: str
    rutuvu: str
    ayana: str


def calculate_calendrical_elements(
    civil_date: date,
    sunrise_jd_ut: float,
    sun_longitude: float,
    tithi_index: int,
    new_moon_sun_longitude: float,
    next_new_moon_sun_longitude: float,
    chaitra_new_moon_jd_ut: float,
    month_convention: str | Enum,
) -> CalendricalElements:
    paksha = calculate_paksha(tithi_index)
    is_adhika_masa = calculate_is_adhika_masa(
        new_moon_sun_longitude,
        next_new_moon_sun_longitude,
    )

    return CalendricalElements(
        samvatsara=calculate_samvatsara(civil_date, sunrise_jd_ut, chaitra_new_moon_jd_ut),
        masa=calculate_masa(new_moon_sun_longitude, paksha, month_convention, is_adhika_masa),
        is_adhika_masa=is_adhika_masa,
        paksha=paksha,
        rutuvu=calculate_rutuvu(sun_longitude),
        ayana=calculate_ayana(sun_longitude),
    )


def calculate_paksha(tithi_index: int) -> str:
    if not 1 <= tithi_index <= 30:
        raise ValueError("Tithi index must be between 1 and 30.")
    return "Shukla" if tithi_index <= 15 else "Krishna"


def calculate_ayana(sun_longitude: float) -> str:
    longitude = sun_longitude % 360.0
    if longitude >= 270.0 or longitude < 90.0:
        return "Uttarayana"
    return "Dakshinayana"


def calculate_rutuvu(sun_longitude: float) -> str:
    return RUTUVU_BY_RASI[calculate_rasi(sun_longitude)]


def calculate_masa(
    new_moon_sun_longitude: float,
    paksha: str,
    month_convention: str | Enum,
    is_adhika_masa: bool = False,
) -> str:
    sun_rasi_at_new_moon = calculate_rasi(new_moon_sun_longitude)
    masa = MASA_BY_NEW_MOON_SUN_RASI[sun_rasi_at_new_moon]

    if _enum_value(month_convention) == "PURNIMANTA" and paksha == "Krishna":
        masa_index = MASA_SEQUENCE.index(masa)
        masa = MASA_SEQUENCE[(masa_index + 1) % len(MASA_SEQUENCE)]

    if is_adhika_masa:
        return f"Adhika {masa}"

    return masa


def calculate_is_adhika_masa(
    previous_new_moon_sun_longitude: float,
    next_new_moon_sun_longitude: float,
) -> bool:
    return calculate_rasi(previous_new_moon_sun_longitude) == calculate_rasi(
        next_new_moon_sun_longitude
    )


def calculate_samvatsara(
    civil_date: date,
    sunrise_jd_ut: float,
    chaitra_new_moon_jd_ut: float,
) -> str:
    saka_year = civil_date.year - 78
    if sunrise_jd_ut < chaitra_new_moon_jd_ut:
        saka_year = civil_date.year - 79

    return SAMVATSARA_NAMES[(saka_year + 11) % 60]


def calculate_rasi(longitude: float) -> int:
    return math.floor((longitude % 360.0) / 30.0)


def _enum_value(value: str | Enum) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)