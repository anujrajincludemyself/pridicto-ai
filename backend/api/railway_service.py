"""
Railway API Service - Fetches train data from RapidAPI
Falls back to mock data if API key is not configured.
"""
import requests
import json
import logging
from django.conf import settings
from .cache_service import get_cached, set_cached

logger = logging.getLogger(__name__)

RAPIDAPI_BASE = "https://indian-railway-irctc.p.rapidapi.com"


def _get_headers():
    return {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }


def get_trains_between_stations(from_code: str, to_code: str, date: str = None):
    """
    Fetch trains between two stations from RapidAPI.
    Returns list of train schedule dicts compatible with graph_engine.
    Falls back to mock data if API key not set.
    """
    if not settings.RAPIDAPI_KEY:
        logger.warning("RAPIDAPI_KEY not set — using mock data")
        return _get_mock_trains_between(from_code, to_code)

    cache_key = f"trains:{from_code}:{to_code}:{date or 'any'}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        url = f"{RAPIDAPI_BASE}/api/trains/v1/train/between-stations"
        params = {"fromStation": from_code, "toStation": to_code}
        if date:
            params["date"] = date  # format: YYYYMMDD

        resp = requests.get(url, headers=_get_headers(), params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        trains = _normalize_rapidapi_response(data, from_code, to_code)
        set_cached(cache_key, trains, ttl_seconds=6 * 3600)  # cache 6 hours
        return trains

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.error("RapidAPI rate limit hit — using mock data")
        else:
            logger.error(f"RapidAPI HTTP error: {e}")
        return _get_mock_trains_between(from_code, to_code)
    except Exception as e:
        logger.error(f"RapidAPI error: {e}")
        return _get_mock_trains_between(from_code, to_code)


def _normalize_rapidapi_response(data, from_code, to_code):
    """Normalize RapidAPI response to our internal format."""
    trains = []
    raw_trains = data.get('data', data.get('trains', []))

    for t in raw_trains:
        train_no = t.get('train_number', t.get('trainNumber', ''))
        train_name = t.get('train_name', t.get('trainName', ''))
        classes = t.get('trainClass', t.get('class_type', ['SL', '3A', '2A', '1A']))
        
        # Build stops from schedule
        schedule = t.get('train_schedule', t.get('schedule', []))
        stops = []
        for stop in schedule:
            stops.append({
                'station_code': stop.get('stationCode', stop.get('station_code', '')),
                'station_name': stop.get('stationName', stop.get('station_name', '')),
                'departure': stop.get('departureTime', stop.get('departure', '--')),
                'arrival': stop.get('arrivalTime', stop.get('arrival', '--')),
                'day': stop.get('dayCount', stop.get('day', 1)),
            })

        if stops:
            trains.append({
                'train_no': train_no,
                'train_name': train_name,
                'classes': classes if isinstance(classes, list) else [classes],
                'stops': stops,
            })

    return trains


def get_station_search(query: str):
    """Search for station codes by name."""
    if not settings.RAPIDAPI_KEY:
        return _mock_station_search(query)

    cache_key = f"station_search:{query.lower()}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        url = f"{RAPIDAPI_BASE}/api/trains/v1/station/search"
        resp = requests.get(url, headers=_get_headers(), params={"query": query}, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        stations = data.get('data', [])
        result = [
            {
                'code': s.get('stationCode', s.get('station_code', '')),
                'name': s.get('stationName', s.get('station_name', '')),
                'state': s.get('state', ''),
            }
            for s in stations
        ]
        set_cached(cache_key, result, ttl_seconds=24 * 3600)
        return result
    except Exception as e:
        logger.error(f"Station search error: {e}")
        return _mock_station_search(query)


def get_live_train_status(train_no: str, date: str):
    """Get live running status of a train."""
    if not settings.RAPIDAPI_KEY:
        return {"status": "API key not configured", "train_no": train_no}

    try:
        url = f"{RAPIDAPI_BASE}/api/trains/v1/train/status"
        resp = requests.get(
            url, headers=_get_headers(),
            params={"trainNumber": train_no, "date": date},
            timeout=8
        )
        resp.raise_for_status()
        return resp.json().get('data', {})
    except Exception as e:
        logger.error(f"Live status error: {e}")
        return {"error": str(e)}


# ─── Mock Data Helpers ──────────────────────────────────────────────────────────

POPULAR_STATIONS = {
    "NEW DELHI": "NDLS",
    "DELHI": "NDLS",
    "MUMBAI": "BCT",
    "MUMBAI CENTRAL": "BCT",
    "HOWRAH": "HWH",
    "KOLKATA": "HWH",
    "PATNA": "PNBE",
    "KOTA": "KOTA",
    "AGRA": "AGC",
    "KANPUR": "CNB",
    "VADODARA": "BRC",
    "PRAYAGRAJ": "ALD",
    "ALLAHABAD": "ALD",
    "MUGHAL SARAI": "MGS",
    "JAIPUR": "JP",
    "CHENNAI": "MAS",
    "BANGALORE": "SBC",
    "HYDERABAD": "SC",
    "PUNE": "PUNE",
    "AHMEDABAD": "ADI",
}

STATION_NAMES = {v: k.title() for k, v in POPULAR_STATIONS.items()}


def _mock_station_search(query: str):
    q = query.upper()
    results = []
    for name, code in POPULAR_STATIONS.items():
        if q in name or q in code:
            results.append({"code": code, "name": name.title(), "state": "India"})
    return results[:10]


def _get_mock_trains_between(from_code: str, to_code: str):
    """Return mock trains that pass through both stations."""
    from .graph_engine import MOCK_TRAINS
    result = []
    for train in MOCK_TRAINS:
        codes = [s['station_code'] for s in train['stops']]
        if from_code in codes and to_code in codes:
            fi = codes.index(from_code)
            ti = codes.index(to_code)
            if fi < ti:
                result.append(train)
    return result
