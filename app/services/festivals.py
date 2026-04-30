from __future__ import annotations


FESTIVAL_MAP = {
    ("Chaitra", "Shukla", "Pratipada"): ["Ugadi", "Gudi Padwa"],
    ("Chaitra", "Shukla", "Navami"): ["Sri Rama Navami"],
    ("Vaisakha", "Shukla", "Tritiya"): ["Akshaya Tritiya"],
    ("Shravana", "Shukla", "Purnima"): ["Raksha Bandhan"],
    ("Shravana", "Krishna", "Ashtami"): ["Krishna Janmashtami"],
    ("Bhadrapada", "Shukla", "Chaturthi"): ["Ganesh Chaturthi"],
    ("Ashvina", "Shukla", "Pratipada"): ["Sharad Navaratri Begins"],
    ("Ashvina", "Shukla", "Dashami"): ["Vijaya Dashami", "Dussehra"],
    ("Kartika", "Krishna", "Amavasya"): ["Diwali", "Deepavali"],
    ("Magha", "Shukla", "Panchami"): ["Vasant Panchami"],
    ("Magha", "Krishna", "Chaturdashi"): ["Maha Shivaratri"],
    ("Phalguna", "Shukla", "Purnima"): ["Holi"],
}


def identify_festivals(masa: str, paksha: str, tithi: str, is_adhika_masa: bool = False) -> list[str]:
    if is_adhika_masa:
        return []

    return list(FESTIVAL_MAP.get((masa, paksha, tithi), []))