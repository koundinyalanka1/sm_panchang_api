from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date


TITHI_NAMES = [
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Purnima",
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Amavasya",
]

NAKSHATRA_NAMES = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

YOGA_NAMES = [
    "Vishkumbha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shula",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
]

REPEATING_KARANA_NAMES = [
    "Bava",
    "Balava",
    "Kaulava",
    "Taitila",
    "Gara",
    "Vanija",
    "Vishti",
]

KARANA_NAMES = [
    "Kimstughna",
    *(REPEATING_KARANA_NAMES * 8),
    "Shakuni",
    "Chatushpada",
    "Naga",
]

VARA_NAMES = {
    0: "Somavara",
    1: "Mangalavara",
    2: "Budhavara",
    3: "Guruvara",
    4: "Shukravara",
    5: "Shanivara",
    6: "Bhanuvara",
}


@dataclass(frozen=True)
class PanchangLimbs:
    tithi: str
    vara: str
    nakshatra: str
    yoga: str
    karana: str


def calculate_panchang_limbs(
    civil_date: date,
    sun_longitude: float,
    moon_longitude: float,
) -> PanchangLimbs:
    return PanchangLimbs(
        tithi=calculate_tithi(sun_longitude, moon_longitude),
        vara=calculate_vara(civil_date),
        nakshatra=calculate_nakshatra(moon_longitude),
        yoga=calculate_yoga(sun_longitude, moon_longitude),
        karana=calculate_karana(sun_longitude, moon_longitude),
    )


def calculate_tithi(sun_longitude: float, moon_longitude: float) -> str:
    return get_tithi_name(calculate_tithi_index(sun_longitude, moon_longitude))


def calculate_tithi_with_paksha(sun_longitude: float, moon_longitude: float) -> str:
    tithi_index = calculate_tithi_index(sun_longitude, moon_longitude)
    return get_tithi_with_paksha(tithi_index)


def calculate_tithi_index(sun_longitude: float, moon_longitude: float) -> int:
    angle = (moon_longitude - sun_longitude) % 360.0
    return _one_based_index(angle, 12.0, 30)


def calculate_vara(civil_date: date) -> str:
    return VARA_NAMES[civil_date.weekday()]


def calculate_nakshatra(moon_longitude: float) -> str:
    return NAKSHATRA_NAMES[calculate_nakshatra_index(moon_longitude) - 1]


def calculate_nakshatra_index(moon_longitude: float) -> int:
    return _one_based_index(moon_longitude % 360.0, 360.0 / 27.0, 27)


def calculate_yoga(sun_longitude: float, moon_longitude: float) -> str:
    return YOGA_NAMES[calculate_yoga_index(sun_longitude, moon_longitude) - 1]


def calculate_yoga_index(sun_longitude: float, moon_longitude: float) -> int:
    angle = (moon_longitude + sun_longitude) % 360.0
    return _one_based_index(angle, 360.0 / 27.0, 27)


def calculate_karana(sun_longitude: float, moon_longitude: float) -> str:
    return KARANA_NAMES[calculate_karana_index(sun_longitude, moon_longitude) - 1]


def calculate_karana_index(sun_longitude: float, moon_longitude: float) -> int:
    angle = (moon_longitude - sun_longitude) % 360.0
    return _one_based_index(angle, 6.0, 60)


def get_next_karana_name(karana_index: int) -> str:
    _validate_one_based_index(karana_index, len(KARANA_NAMES), "Karana")
    return KARANA_NAMES[karana_index % len(KARANA_NAMES)]


def get_next_tithi_with_paksha(tithi_index: int) -> str:
    return get_tithi_with_paksha((tithi_index % len(TITHI_NAMES)) + 1)


def get_next_yoga_name(yoga_index: int) -> str:
    _validate_one_based_index(yoga_index, len(YOGA_NAMES), "Yoga")
    return YOGA_NAMES[yoga_index % len(YOGA_NAMES)]


def get_tithi_name(tithi_index: int) -> str:
    _validate_one_based_index(tithi_index, len(TITHI_NAMES), "Tithi")
    return TITHI_NAMES[tithi_index - 1]


def get_tithi_with_paksha(tithi_index: int) -> str:
    return f"{get_tithi_paksha(tithi_index)} {get_tithi_name(tithi_index)}"


def get_tithi_paksha(tithi_index: int) -> str:
    _validate_one_based_index(tithi_index, len(TITHI_NAMES), "Tithi")
    return "Shukla" if tithi_index <= 15 else "Krishna"


def _validate_one_based_index(index: int, total_segments: int, segment_name: str) -> None:
    if not 1 <= index <= total_segments:
        raise ValueError(f"{segment_name} index must be between 1 and {total_segments}.")


def _one_based_index(angle: float, arc_degrees: float, total_segments: int) -> int:
    index = math.floor((angle % 360.0) / arc_degrees) + 1
    return min(max(index, 1), total_segments)
