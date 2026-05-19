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
RAPIDAPI_SEAT_BASE = "https://indian-railway-seat-availability.p.rapidapi.com"


def _get_headers():
    return {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }


def _get_seat_headers():
    return {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_SEAT_HOST,
        "Content-Type": "application/json",
    }


def _seat_status_is_available(status_value, available_seats_value=None):
    status_text = str(status_value or '').upper().strip()

    if available_seats_value not in (None, '', 'NA', 'N/A'):
        try:
            if int(str(available_seats_value)) > 0:
                return True
        except Exception:
            pass

    if not status_text:
        return False

    if 'WL' in status_text or 'WAIT' in status_text or 'RAC' in status_text:
        return False

    return 'AVAILABLE' in status_text or 'AVL' in status_text


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


def get_seat_availability(train_no: str, from_code: str, to_code: str, date: str, quota: str = 'GN', class_code: str = 'SL'):
    """Get seat availability for a train."""
    if not settings.RAPIDAPI_KEY:
        return {
            "available": False,
            "provider": "mock",
            "message": "RAPIDAPI_KEY not configured",
            "train_no": train_no,
            "from": from_code,
            "to": to_code,
            "date": date,
            "quota": quota,
            "class_code": class_code,
            "seats": [],
        }

    cache_key = f"seat:{train_no}:{from_code}:{to_code}:{date}:{quota}:{class_code}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        url = f"{RAPIDAPI_SEAT_BASE}/v1/seat-availability"
        params = {
            "trainNumber": train_no,
            "train_no": train_no,
            "fromStation": from_code,
            "from": from_code,
            "toStation": to_code,
            "to": to_code,
            "date": date,
            "journeyDate": date,
            "quota": quota,
            "classCode": class_code,
            "class": class_code,
        }

        resp = requests.get(url, headers=_get_seat_headers(), params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()

        result = _normalize_seat_availability_response(data, train_no, from_code, to_code, date, quota, class_code)
        set_cached(cache_key, result, ttl_seconds=15 * 60)
        return result
    except Exception as e:
        logger.error(f"Seat availability error: {e}")
        if settings.INDIAN_RAIL_API_KEY:
            try:
                url = (
                    f"https://indianrailapi.com/api/v2/SeatAvailability/apikey/{settings.INDIAN_RAIL_API_KEY}"
                    f"/TrainNumber/{train_no}/From/{from_code}/To/{to_code}/Date/{date}/Quota/{quota}/Class/{class_code}"
                )
                resp = requests.get(url, timeout=12)
                resp.raise_for_status()
                data = resp.json()
                result = _normalize_seat_availability_response(data, train_no, from_code, to_code, date, quota, class_code)
                set_cached(cache_key, result, ttl_seconds=15 * 60)
                return result
            except Exception as fallback_error:
                logger.error(f"Seat availability fallback error: {fallback_error}")

        return {
            "available": False,
            "provider": "error",
            "error": str(e),
            "train_no": train_no,
            "from": from_code,
            "to": to_code,
            "date": date,
            "quota": quota,
            "class_code": class_code,
            "seats": [],
        }


def _normalize_seat_availability_response(data, train_no, from_code, to_code, date, quota, class_code):
    """Normalize different provider response shapes into one structure."""
    candidates = []
    if isinstance(data, dict):
        for key in ('data', 'result', 'availability', 'train'):
            value = data.get(key)
            if isinstance(value, list):
                candidates = value
                break
            if isinstance(value, dict):
                candidates = [value]
                break
        if not candidates:
            candidates = [data]

    seats = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        seats.extend(_extract_seat_rows(item))

    if not seats and isinstance(data, dict):
        seats.extend(_extract_seat_rows(data))

    available = any(_seat_status_is_available(seat.get('status'), seat.get('available_seats')) for seat in seats)

    return {
        "available": available,
        "provider": "rapidapi-seat-availability",
        "train_no": train_no,
        "from": from_code,
        "to": to_code,
        "date": date,
        "quota": quota,
        "class_code": class_code,
        "seats": seats,
        "raw": data,
    }


def _extract_seat_rows(payload):
    rows = []
    for key in ('availability', 'classes', 'seats', 'results', 'items', 'data', 'result'):
        value = payload.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    rows.append({
                        'status': item.get('status', item.get('seat_status', item.get('availability_status', 'unknown'))),
                        'date': item.get('date', item.get('journey_date', '')),
                        'class_code': item.get('class', item.get('classCode', item.get('class_code', ''))),
                        'quota': item.get('quota', item.get('quotaCode', item.get('quota_code', ''))),
                        'available_seats': item.get('available_seats', item.get('seats_available', item.get('available', ''))),
                        'fare': item.get('fare', item.get('price', '')),
                        'source_station': item.get('from', item.get('fromStation', item.get('source_station', ''))),
                        'destination_station': item.get('to', item.get('toStation', item.get('destination_station', ''))),
                    })
            break

    if not rows and any(k in payload for k in ('status', 'available_seats', 'fare')):
        rows.append({
            'status': payload.get('status', 'unknown'),
            'date': payload.get('date', payload.get('journey_date', '')),
            'class_code': payload.get('class', payload.get('classCode', payload.get('class_code', ''))),
            'quota': payload.get('quota', payload.get('quotaCode', payload.get('quota_code', ''))),
            'available_seats': payload.get('available_seats', payload.get('seats_available', payload.get('available', ''))),
            'fare': payload.get('fare', payload.get('price', '')),
            'source_station': payload.get('from', payload.get('fromStation', payload.get('source_station', ''))),
            'destination_station': payload.get('to', payload.get('toStation', payload.get('destination_station', ''))),
        })

    return rows


def filter_routes_with_available_seats(routes: list, date: str, quota: str = 'GN'):
    """Annotate routes with seat checks and keep only routes with live seat availability."""
    filtered_routes = []
    provider_errors = 0
    routes_checked = 0

    for route in routes:
        routes_checked += 1
        route_checks = []
        all_available = True

        for leg in route.get('legs', []):
            train_no = leg.get('train_no', '')
            from_code = leg.get('from_code') or leg.get('from') or ''
            to_code = leg.get('to_code') or leg.get('to') or ''
            classes = leg.get('classes') or ['SL']
            class_code = classes[0] if isinstance(classes, list) and classes else 'SL'

            seat_result = get_seat_availability(train_no, from_code, to_code, date, quota, class_code)
            route_checks.append({
                'train_no': train_no,
                'from_code': from_code,
                'to_code': to_code,
                'class_code': class_code,
                'available': seat_result.get('available', False),
                'seats': seat_result.get('seats', []),
                'provider': seat_result.get('provider', 'unknown'),
                'raw_status': seat_result.get('seats', [{}])[0].get('status') if seat_result.get('seats') else seat_result.get('status'),
                'error': seat_result.get('error'),
                'date': seat_result.get('date', date),
            })

            if seat_result.get('provider') == 'error' or seat_result.get('error'):
                provider_errors += 1

            if not seat_result.get('available'):
                all_available = False
                break

        if all_available and route_checks:
            annotated_route = dict(route)
            annotated_route['seat_available'] = True
            annotated_route['seat_checks'] = route_checks
            filtered_routes.append(annotated_route)

    reason = None
    if not filtered_routes:
        reason = 'seat_api_unavailable' if provider_errors else 'no_live_seats_found'

    return {
        'routes': filtered_routes,
        'routes_checked': routes_checked,
        'provider_errors': provider_errors,
        'reason': reason,
    }


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
