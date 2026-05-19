import os
import requests
import json
from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pridicto.settings')
django.setup()

def test_api():
    api_key = getattr(settings, 'RAPIDAPI_KEY', None)
    api_host = getattr(settings, 'RAPIDAPI_HOST', None)
    
    if not api_key:
        print('RAPIDAPI_KEY not configured')
        return

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': api_host
    }

    # 1. Station search
    print('Testing Station Search (Delhi)...')
    url_search = f'https://{api_host}/api/v1/searchStation'
    params_search = {'query': 'Delhi'}
    try:
        resp1 = requests.get(url_search, headers=headers, params=params_search, timeout=10)
        print(f'Status: {resp1.status_code}')
        print(f'Headers: { {k: v for k, v in resp1.headers.items() if "ratelimit" in k.lower()} }')
        print(f'Body: {resp1.text[:300]}...')
    except Exception as e:
        print(f'Error: {e}')

    print('\nTesting Between Stations (NDLS to BCT on 2026-05-16)...')
    url_between = f'https://{api_host}/api/v3/trainBetweenStations'
    params_between = {'fromStationCode': 'NDLS', 'toStationCode': 'BCT', 'dateOfJourney': '20260516'}
    try:
        resp2 = requests.get(url_between, headers=headers, params=params_between, timeout=10)
        print(f'Status: {resp2.status_code}')
        print(f'Headers: { {k: v for k, v in resp2.headers.items() if "ratelimit" in k.lower()} }')
        print(f'Body: {resp2.text[:300]}...')
        
        if resp2.status_code == 200 and 'data' in resp2.json():
            print('\nRecommendation: Continue using RapidAPI provider.')
        else:
            print('\nRecommendation: Fall back to mock data.')
    except Exception as e:
        print(f'Error: {e}')
        print('\nRecommendation: Fall back to mock data.')

if __name__ == "__main__":
    test_api()
