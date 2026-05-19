import os
import django
from django.test import Client
from api.railway_service import get_seat_availability

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pridicto.settings")
django.setup()

def test_seat_availability():
    print("--- Part 1: get_seat_availability ---")
    trains = [
        {"no": "12001", "from": "NDLS", "to": "KOTA"},
        {"no": "12302", "from": "NDLS", "to": "HWH"},
        {"no": "12953", "from": "NDLS", "to": "BCT"},
    ]
    date = "20260516"
    for t in trains:
        try:
            res = get_seat_availability(t["no"], t["from"], t["to"], date, "SL")
            # Handle potential list or dict response based on common patterns
            if isinstance(res, list):
                for item in res:
                    print(f"Train {t['no']}: Provider={item.get('provider')}, Available={item.get('available')}, Status={item.get('status')}")
            elif isinstance(res, dict):
                 print(f"Train {t['no']}: Provider={res.get('provider')}, Available={res.get('available')}, Status={res.get('status')}")
            else:
                print(f"Train {t['no']}: Unexpected response type {type(res)}")
        except Exception as e:
            print(f"Train {t['no']}: Error {e}")

def test_search_endpoint():
    print("\n--- Part 2: Search Endpoint ---")
    c = Client()
    url = "/api/routes/search/?from=NDLS&to=BCT&date=20260516"
    response = c.get(url)
    if response.status_code == 200:
        data = response.json()
        routes = data.get("routes", [])
        print(f"routes_count: {len(routes)}")
        if not routes:
            print("Zero routes returned (possible seat filter).")
        for r in routes:
            train_no = r.get("train_number") or r.get("number")
            seat_avail = "seat_availability" in r
            seat_checks = "seat_checks" in r
            print(f"Train {train_no}: seat_available={seat_avail}, seat_checks={seat_checks}")
    else:
        print(f"Search failed with status {response.status_code}")

if __name__ == '__main__':
    test_seat_availability()
    test_search_endpoint()
