from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyHeader

from app.models import (
    AyanamsaName,
    AstronomicalResponse,
    CalendricalResponse,
    LocationResponse,
    MonthConvention,
    PanchangRequest,
    PanchangLimbsResponse,
    PanchangResponse,
)
from app.services.astronomy import AstronomyCalculationError, CelestialBody, SwissEphemerisAstronomyService
from app.services.calendrical import calculate_calendrical_elements
from app.services.festivals import identify_festivals
from app.services.panchang import (
    calculate_karana_index,
    calculate_panchang_limbs,
    calculate_tithi_index,
    calculate_yoga_index,
    get_next_karana_name,
    get_next_tithi_with_paksha,
    get_next_yoga_name,
)


app = FastAPI(
    title="SM Panchang API",
    version="1.1.0",
    description="Swiss Ephemeris based Hindu Panchang API with Pancha-Anga, calendrical layers, festivals, and edge-case mechanics.",
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    valid_api_key = os.getenv("PANCHANG_API_KEY", "my-local-dev-key")

    if api_key != valid_api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")

    return api_key


@lru_cache(maxsize=1)
def get_astronomy_service() -> SwissEphemerisAstronomyService:
    return SwissEphemerisAstronomyService()


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/v1/panchang",
    response_model=PanchangResponse,
    tags=["panchang"],
    dependencies=[Depends(get_api_key)],
)
@app.post(
    "/api/v1/phase1/astronomy",
    response_model=PanchangResponse,
    tags=["phase-1"],
)
def calculate_panchang(request: PanchangRequest) -> PanchangResponse:
    if request.preferences.ayanamsa != AyanamsaName.LAHIRI:
        raise HTTPException(status_code=422, detail="This API currently supports only LAHIRI ayanamsa.")

    service = get_astronomy_service()

    try:
        result = service.calculate_phase1(
            civil_date=request.date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_name=request.timezone,
        )
        panchang = calculate_panchang_limbs(
            civil_date=request.date,
            sun_longitude=result.sun.sidereal_longitude,
            moon_longitude=result.moon.sidereal_longitude,
        )
        tithi_index = calculate_tithi_index(
            sun_longitude=result.sun.sidereal_longitude,
            moon_longitude=result.moon.sidereal_longitude,
        )
        yoga_index = calculate_yoga_index(
            sun_longitude=result.sun.sidereal_longitude,
            moon_longitude=result.moon.sidereal_longitude,
        )
        karana_index = calculate_karana_index(
            sun_longitude=result.sun.sidereal_longitude,
            moon_longitude=result.moon.sidereal_longitude,
        )
        previous_new_moon_jd = service.find_previous_new_moon(result.sunrise.julian_day_ut)
        next_new_moon_jd = service.find_next_new_moon(result.sunrise.julian_day_ut)
        tithi_end_jd = service.find_tithi_end(result.sunrise.julian_day_ut)
        nakshatra_end_jd = service.find_nakshatra_end(result.sunrise.julian_day_ut)
        yoga_end_jd = service.find_yoga_end(result.sunrise.julian_day_ut)
        karana_end_jd = service.find_karana_end(result.sunrise.julian_day_ut)
        _tithi_end_utc, tithi_end_local = service.from_julian_day_ut(tithi_end_jd, request.timezone)
        _nakshatra_end_utc, nakshatra_end_local = service.from_julian_day_ut(
            nakshatra_end_jd,
            request.timezone,
        )
        _yoga_end_utc, yoga_end_local = service.from_julian_day_ut(yoga_end_jd, request.timezone)
        _karana_end_utc, karana_end_local = service.from_julian_day_ut(
            karana_end_jd,
            request.timezone,
        )
        new_moon_sun = service.get_sidereal_longitude(CelestialBody.SUN, previous_new_moon_jd)
        next_new_moon_sun = service.get_sidereal_longitude(CelestialBody.SUN, next_new_moon_jd)
        following_new_moon_sun_longitude = None
        if request.preferences.month_convention == MonthConvention.PURNIMANTA:
            following_new_moon_jd = service.find_next_new_moon(next_new_moon_jd + 1.0)
            following_new_moon_sun = service.get_sidereal_longitude(
                CelestialBody.SUN,
                following_new_moon_jd,
            )
            following_new_moon_sun_longitude = following_new_moon_sun.sidereal_longitude

        chaitra_new_moon_jd = service.find_chaitra_new_moon(request.date.year, request.timezone)
        calendrical = calculate_calendrical_elements(
            civil_date=request.date,
            sunrise_jd_ut=result.sunrise.julian_day_ut,
            sun_longitude=result.sun.sidereal_longitude,
            tithi_index=tithi_index,
            new_moon_sun_longitude=new_moon_sun.sidereal_longitude,
            next_new_moon_sun_longitude=next_new_moon_sun.sidereal_longitude,
            chaitra_new_moon_jd_ut=chaitra_new_moon_jd,
            month_convention=request.preferences.month_convention,
            following_new_moon_sun_longitude=following_new_moon_sun_longitude,
        )
        festivals = identify_festivals(
            masa=calendrical.masa,
            paksha=calendrical.paksha,
            tithi=panchang.tithi,
            is_adhika_masa=calendrical.is_adhika_masa,
            month_convention=request.preferences.month_convention,
        )
    except (AstronomyCalculationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PanchangResponse(
        location=LocationResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone,
        ),
        astronomical=AstronomicalResponse(
            sunrise=_format_clock_time(result.sunrise.local_time, request.date),
            sunset=_format_clock_time(result.sunset.local_time, request.date),
        ),
        panchang=PanchangLimbsResponse(
            tithi=f"{calendrical.paksha} {panchang.tithi}",
            tithi_end_time=_format_clock_time(tithi_end_local, request.date),
            next_tithi=get_next_tithi_with_paksha(tithi_index),
            vara=panchang.vara,
            nakshatra=panchang.nakshatra,
            nakshatra_end_time=_format_clock_time(nakshatra_end_local, request.date),
            yoga=panchang.yoga,
            yoga_end_time=_format_clock_time(yoga_end_local, request.date),
            next_yoga=get_next_yoga_name(yoga_index),
            karana=panchang.karana,
            karana_end_time=_format_clock_time(karana_end_local, request.date),
            next_karana=get_next_karana_name(karana_index),
        ),
        calendrical=CalendricalResponse(
            samvatsara=calendrical.samvatsara,
            masa=calendrical.masa,
            is_adhika_masa=calendrical.is_adhika_masa,
            paksha=calendrical.paksha,
            rutuvu=calendrical.rutuvu,
            ayana=calendrical.ayana,
        ),
        festivals=festivals,
    )


calculate_phase1_astronomy = calculate_panchang


def _format_clock_time(moment: datetime, reference_date: date | None = None) -> str:
    rounded = moment + timedelta(seconds=30)
    formatted_time = rounded.strftime("%I:%M %p")

    if reference_date is not None and rounded.date() > reference_date:
        return f"{formatted_time} (Next Day)"

    return formatted_time
