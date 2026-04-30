from __future__ import annotations

from datetime import date as Date
from enum import Enum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AyanamsaName(str, Enum):
    LAHIRI = "LAHIRI"


class MonthConvention(str, Enum):
    AMANTA = "AMANTA"
    PURNIMANTA = "PURNIMANTA"


class PanchangPreferences(StrictBaseModel):
    ayanamsa: AyanamsaName = Field(
        default=AyanamsaName.LAHIRI,
        description="Sidereal ayanamsa. Phase 1 implements Lahiri/Chitra Paksha.",
    )
    month_convention: MonthConvention = Field(
        default=MonthConvention.AMANTA,
        description="Lunar month naming convention reserved for later calendrical phases.",
    )


class PanchangRequest(StrictBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "date": "2026-05-09",
                "latitude": 17.5167,
                "longitude": 78.4667,
                "timezone": "Asia/Kolkata",
                "preferences": {
                    "ayanamsa": "LAHIRI",
                    "month_convention": "AMANTA",
                },
            }
        }
    )

    date: Date = Field(description="Civil date at the requested location.")
    latitude: float = Field(ge=-90.0, le=90.0, description="Latitude in decimal degrees.")
    longitude: float = Field(
        ge=-180.0,
        le=180.0,
        description="Longitude in decimal degrees, east positive and west negative.",
    )
    timezone: str = Field(description="IANA timezone name, for example Asia/Kolkata.")
    preferences: PanchangPreferences = Field(default_factory=PanchangPreferences)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown IANA timezone: {value}") from exc
        return value


class LocationResponse(StrictBaseModel):
    latitude: float
    longitude: float
    timezone: str


class AstronomicalResponse(StrictBaseModel):
    sunrise: str
    sunset: str


class CalendricalResponse(StrictBaseModel):
    samvatsara: str
    masa: str
    is_adhika_masa: bool
    paksha: str
    rutuvu: str
    ayana: str


class PanchangLimbsResponse(StrictBaseModel):
    tithi: str
    tithi_end_time: str
    vara: str
    nakshatra: str
    yoga: str
    karana: str


class PanchangResponse(StrictBaseModel):
    location: LocationResponse
    astronomical: AstronomicalResponse
    panchang: PanchangLimbsResponse
    calendrical: CalendricalResponse
    festivals: list[str]
