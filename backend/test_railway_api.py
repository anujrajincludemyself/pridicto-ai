import os
import django
from unittest.mock import patch, MagicMock
from django.test import Client

def run_test():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pridicto.settings')
    django.setup()

    from api import railway_service
    from api.railway_service import get_seat_availability

    # 1. Monkeypatch settings
    railway_service.settings.INDIAN_RAIL_API_KEY = 'fake-api-key'

    # 2. Mock requests.get
    fake_response_data = {
        'response_code': 200,
        'train': {'name': 'SHATABDI EXP', 'number': '12001'},
        'from_station': {'name': 'NEW DELHI', 'code': 'NDLS'},
        'to_station': {'name': 'MUMBAI CENTRAL', 'code': 'BCT'},
        'availability': [{'date': '16-05-2026', 'status': 'AVAILABLE 0100'}]
    }
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_response_data

        # 3. Call service directly
        print("Calling get_seat_availability directly...")
        result = get_seat_availability('12001','NDLS','BCT','20260516','GN','SL')
        print(f"Service Result: {result}")

        # 4. Use Test Client
        client = Client()
        print("\nCalling API via Django Test Client...")
        response = client.get('/api/train/seat-availability/', {
            'train_no': '12001',
            'from_stn': 'NDLS',
            'to_stn': 'BCT',
            'date': '20260516',
            'quota': 'GN',
            'class_code': 'SL'
        })
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"JSON Keys: {list(response.json().keys())}")
        else:
            print(f"Response Content: {response.content}")

if __name__ == '__main__':
    run_test()
