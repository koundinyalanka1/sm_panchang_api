from __future__ import annotations

from enum import Enum


SHARED_FESTIVAL_MAP = {
    ("Chaitra", "Shukla", "Pratipada"): ["Ugadi", "Gudi Padwa"],
    ("Chaitra", "Shukla", "Navami"): ["Sri Rama Navami"],
    ("Vaisakha", "Shukla", "Tritiya"): ["Akshaya Tritiya"],
    ("Shravana", "Shukla", "Purnima"): ["Raksha Bandhan"],
    ("Bhadrapada", "Shukla", "Chaturthi"): ["Ganesh Chaturthi"],
    ("Ashvina", "Shukla", "Pratipada"): ["Sharad Navaratri Begins"],
    ("Ashvina", "Shukla", "Dashami"): ["Vijaya Dashami", "Dussehra"],
    ("Magha", "Shukla", "Panchami"): ["Vasant Panchami"],
    ("Phalguna", "Shukla", "Purnima"): ["Holi"],
}

AMANTA_FESTIVAL_MAP = {
    **SHARED_FESTIVAL_MAP,
    ("Shravana", "Krishna", "Ashtami"): ["Krishna Janmashtami"],
    ("Kartika", "Krishna", "Amavasya"): ["Diwali", "Deepavali"],
    ("Magha", "Krishna", "Chaturdashi"): ["Maha Shivaratri"],
}

PURNIMANTA_FESTIVAL_MAP = {
    **SHARED_FESTIVAL_MAP,
    ("Bhadrapada", "Krishna", "Ashtami"): ["Krishna Janmashtami"],
    ("Kartika", "Krishna", "Amavasya"): ["Diwali", "Deepavali"],
    ("Phalguna", "Krishna", "Chaturdashi"): ["Maha Shivaratri"],
}

FESTIVAL_MAPS = {
    "AMANTA": AMANTA_FESTIVAL_MAP,
    "PURNIMANTA": PURNIMANTA_FESTIVAL_MAP,
}


def identify_festivals(
    masa: str,
    paksha: str,
    tithi: str,
    is_adhika_masa: bool = False,
    month_convention: str | Enum = "AMANTA",
) -> list[str]:
    if is_adhika_masa:
        return []

    festival_map = FESTIVAL_MAPS.get(_enum_value(month_convention), AMANTA_FESTIVAL_MAP)
    return list(festival_map.get((masa, paksha, tithi), []))


def _enum_value(value: str | Enum) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)
