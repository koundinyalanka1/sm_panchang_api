# SM Panchang API

Phase 5 builds on the astronomical foundation for a dynamic Hindu Panchang API. It calculates the Pancha-Anga limbs, cultural calendrical layer, core festival identification, Adhika Masa, and exact Tithi end times from Swiss Ephemeris based sidereal Sun and Moon longitudes.

## What The API Provides

- FastAPI application instance in `app.main:app`.
- Pydantic request/response models for date, timezone, latitude, longitude, and preferences.
- Timezone-aware local datetime to Julian Day UT conversion.
- Sunrise and sunset for the requested civil date/location using Swiss Ephemeris, atmospheric refraction, and the center of the Sun's disk.
- Apparent geocentric tropical longitudes of the Sun and Moon at local sunrise.
- Lahiri/Chitra Paksha ayanamsa subtraction to return sidereal, Nirayana longitudes.
- Tithi, Vara, Nakshatra, Yoga, and Karana at local sunrise.
- Paksha, Ayana, Rutuvu, Amanta/Purnimanta Masa, and Samvatsara.
- Adhika Masa detection from consecutive New Moon Sun Rasis.
- Exact local Tithi end time using bounded root finding.
- Festival identification from Masa, Paksha, and Tithi.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Swiss Ephemeris Files

`pyswisseph` is the Python binding for Swiss Ephemeris. This service requires Swiss Ephemeris `.se1` data files and rejects silent fallback to the lower-precision built-in Moshier ephemeris.

1. Download Swiss Ephemeris data files from the public Swiss Ephemeris repository listed by Astrodienst: <https://github.com/aloistr/swisseph/tree/master/ephe>
2. Create a local ephemeris directory:

```bash
mkdir -p ephe
```

3. For the bundled example date in 2026, place at least these files in `ephe/`:

- `sepl_18.se1` for planetary/Sun calculations covering 1800-2399.
- `semo_18.se1` for Moon calculations covering 1800-2399.

You can fetch those two files directly with:

```bash
curl -fL -o ephe/sepl_18.se1 https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/sepl_18.se1
curl -fL -o ephe/semo_18.se1 https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/semo_18.se1
```

4. Export the directory before running the app:

```bash
export SWISSEPH_EPHE_PATH="$PWD/ephe"
```

For broader historical/future support, add the matching `sepl_*.se1` and `semo_*.se1` files for the date ranges your API will serve.

## Run The API

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive OpenAPI UI.

## Default Request

The same payload is stored at `examples/phase1_request.json`.

```json
{
  "date": "2026-05-09",
  "latitude": 17.5167,
  "longitude": 78.4667,
  "timezone": "Asia/Kolkata",
  "preferences": {
    "ayanamsa": "LAHIRI",
    "month_convention": "AMANTA"
  }
}
```

Call the endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/panchang \
  -H 'Content-Type: application/json' \
  --data @examples/phase1_request.json
```

The response uses the final Phase 5 contract:

```json
{
  "location": {
    "latitude": 17.5167,
    "longitude": 78.4667,
    "timezone": "Asia/Kolkata"
  },
  "astronomical": {
    "sunrise": "05:48 AM",
    "sunset": "06:38 PM"
  },
  "panchang": {
    "tithi": "Krishna Saptami",
    "tithi_end_time": "02:03 PM",
    "next_tithi": "Krishna Ashtami",
    "vara": "Shanivara",
    "nakshatra": "Shravana",
    "nakshatra_end_time": "11:25 PM",
    "yoga": "Shukla",
    "yoga_end_time": "02:35 AM",
    "next_yoga": "Brahma",
    "karana": "Bava",
    "karana_end_time": "02:03 PM",
    "next_karana": "Balava"
  },
  "calendrical": {
    "samvatsara": "Parabhava",
    "masa": "Vaisakha",
    "is_adhika_masa": false,
    "paksha": "Krishna",
    "rutuvu": "Vasanta",
    "ayana": "Uttarayana"
  },
  "festivals": []
}
```

Or run the direct smoke script:

```bash
python scripts/smoke_panchang.py
```

## Calculation Notes

- Panchang limbs are calculated at the returned local sunrise.
- Sidereal longitudes are normalized to `[0, 360)` degrees.
- Tithi and Karana use `((Moon - Sun) % 360)`.
- Yoga uses `((Moon + Sun) % 360)`.
- Nakshatra uses `(Moon % 360)`.
- Paksha is derived from the 1-based Tithi index.
- Tithi, Nakshatra, Yoga, and Karana end times are found by bracketing and bisecting their next segment boundaries from the sunrise state.
- Ayana and Rutuvu are derived from the Sun's sidereal longitude at sunrise.
- Amanta Masa is derived from the Sun's sidereal Rasi at the exact previous New Moon.
- Purnimanta Shukla Paksha uses the same lunation as Amanta; Purnimanta Krishna Paksha is anchored to the next New Moon lunation so month names, skipped months, and Adhika Masa are convention-aware.
- Adhika Masa is true when the Sun's Rasi is the same at the pair of New Moons that define the displayed Masa; the displayed Masa is prefixed with `Adhika `.
- Samvatsara uses the Saka year and the Chaitra Shukla Pratipada anchor found from the Chaitra New Moon.
- Festivals are looked up from the final Masa, Paksha, and bare Tithi name; Adhika Masa always returns `[]`.
- Longitude input is east-positive, matching Swiss Ephemeris geographic coordinates.
- Altitude is fixed at sea level because altitude is not part of the requested input contract.