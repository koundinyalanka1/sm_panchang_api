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
    return TITHI_NAMES[calculate_tithi_index(sun_longitude, moon_longitude) - 1]


def calculate_tithi_with_paksha(sun_longitude: float, moon_longitude: float) -> str:
    tithi_index = calculate_tithi_index(sun_longitude, moon_longitude)
    paksha = "Shukla" if tithi_index <= 15 else "Krishna"
    return f"{paksha} {TITHI_NAMES[tithi_index - 1]}"


def calculate_tithi_index(sun_longitude: float, moon_longitude: float) -> int:
    angle = (moon_longitude - sun_longitude) % 360.0
    return _one_based_index(angle, 12.0, 30)


def calculate_vara(civil_date: date) -> str:
    return VARA_NAMES[civil_date.weekday()]


def calculate_nakshatra(moon_longitude: float) -> str:
    nakshatra_index = _one_based_index(moon_longitude % 360.0, 360.0 / 27.0, 27)
    return NAKSHATRA_NAMES[nakshatra_index - 1]


def calculate_yoga(sun_longitude: float, moon_longitude: float) -> str:
    angle = (moon_longitude + sun_longitude) % 360.0
    yoga_index = _one_based_index(angle, 360.0 / 27.0, 27)
    return YOGA_NAMES[yoga_index - 1]


def calculate_karana(sun_longitude: float, moon_longitude: float) -> str:
    angle = (moon_longitude - sun_longitude) % 360.0
    karana_index = _one_based_index(angle, 6.0, 60)

    if karana_index == 1:
        return "Kimstughna"
    if karana_index == 58:
        return "Shakuni"
    if karana_index == 59:
        return "Chatushpada"
    if karana_index == 60:
        return "Naga"

    return REPEATING_KARANA_NAMES[(karana_index - 2) % len(REPEATING_KARANA_NAMES)]


def _one_based_index(angle: float, arc_degrees: float, total_segments: int) -> int:
    index = math.floor((angle % 360.0) / arc_degrees) + 1
    return min(max(index, 1), total_segments)