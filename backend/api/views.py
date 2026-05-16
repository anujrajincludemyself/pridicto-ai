"""
Pridicto API Views
"""
import logging
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .graph_engine import find_routes, MOCK_TRAINS
from .railway_service import get_trains_between_stations, get_station_search, get_live_train_status
from .ai_service import parse_search_intent, format_routes_with_ai

logger = logging.getLogger(__name__)


@api_view(['GET'])
def health_check(request):
    """API health check endpoint."""
    return Response({
        'status': 'ok',
        'service': 'Pridicto API',
        'timestamp': datetime.now().isoformat(),
    })


@api_view(['GET'])
def search_routes(request):
    """
    Search for train routes between two stations.
    
    Query params:
      - from: origin station code (e.g. NDLS)
      - to: destination station code (e.g. BCT)
      - date: travel date YYYYMMDD (optional, defaults to today)
      - max_hops: max connections (optional, default 2)
    """
    from_code = request.GET.get('from', '').upper().strip()
    to_code = request.GET.get('to', '').upper().strip()
    date = request.GET.get('date', datetime.now().strftime('%Y%m%d'))
    max_hops = int(request.GET.get('max_hops', 2))

    if not from_code or not to_code:
        return Response(
            {'error': 'Both "from" and "to" station codes are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if from_code == to_code:
        return Response(
            {'error': 'Origin and destination cannot be the same.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Fetch train schedules (from API or mock)
        train_schedules = get_trains_between_stations(from_code, to_code, date)
        
        # If not enough direct trains, also fetch via common junction stations
        if len(train_schedules) < 3:
            # Add all mock trains for graph completeness
            all_trains = list(train_schedules)
            from .graph_engine import MOCK_TRAINS
            existing_nos = {t['train_no'] for t in all_trains}
            for t in MOCK_TRAINS:
                if t['train_no'] not in existing_nos:
                    all_trains.append(t)
        else:
            all_trains = train_schedules

        # Run graph algorithm
        routes = find_routes(
            all_trains,
            origin=from_code,
            destination=to_code,
            max_hops=max_hops,
            max_results=8,
        )

        return Response({
            'success': True,
            'from': from_code,
            'to': to_code,
            'date': date,
            'routes_count': len(routes),
            'routes': routes,
            'data_source': 'api' if hasattr(train_schedules, '__len__') and len(train_schedules) > 0 else 'mock',
        })

    except Exception as e:
        logger.exception(f"Route search error: {e}")
        return Response(
            {'error': 'Route search failed. Please try again.', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def ai_search(request):
    """
    AI-powered natural language search.
    
    Body: { "query": "trains from Delhi to Mumbai tomorrow morning" }
    """
    query = request.data.get('query', '').strip()
    
    if not query:
        return Response(
            {'error': 'Query is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Parse intent with Claude
        intent = parse_search_intent(query)
        
        if not intent.get('is_valid'):
            return Response({
                'success': False,
                'error': intent.get('error', 'Could not understand the query. Please specify origin and destination.'),
                'intent': intent,
            })

        from_code = intent.get('origin', '').upper().strip()
        to_code = intent.get('destination', '').upper().strip()
        date = intent.get('date', datetime.now().strftime('%Y%m%d'))

        # Get train schedules
        train_schedules = get_trains_between_stations(from_code, to_code, date)
        all_trains = list(train_schedules)
        from .graph_engine import MOCK_TRAINS
        existing_nos = {t['train_no'] for t in all_trains}
        for t in MOCK_TRAINS:
            if t['train_no'] not in existing_nos:
                all_trains.append(t)

        # Find routes
        routes = find_routes(all_trains, origin=from_code, destination=to_code, max_hops=2)

        # Format with AI
        ai_summary = format_routes_with_ai(routes, query)

        return Response({
            'success': True,
            'query': query,
            'intent': intent,
            'ai_summary': ai_summary,
            'routes': routes,
            'routes_count': len(routes),
        })

    except Exception as e:
        logger.exception(f"AI search error: {e}")
        return Response(
            {'error': 'AI search failed.', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def station_search(request):
    """
    Search for stations by name.
    Query param: q (search query)
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return Response({'stations': []})
    
    stations = get_station_search(query)
    return Response({'stations': stations})


@api_view(['GET'])
def train_status(request):
    """
    Get live train status.
    Query params: train_no, date (YYYYMMDD)
    """
    train_no = request.GET.get('train_no', '').strip()
    date = request.GET.get('date', datetime.now().strftime('%Y%m%d'))
    
    if not train_no:
        return Response(
            {'error': 'train_no is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    status_data = get_live_train_status(train_no, date)
    return Response({'train_no': train_no, 'status': status_data})


@api_view(['GET'])
def popular_routes(request):
    """Return a list of popular train routes in India."""
    routes = [
        {"from": "NDLS", "from_name": "New Delhi", "to": "BCT", "to_name": "Mumbai Central", "label": "Delhi → Mumbai"},
        {"from": "NDLS", "from_name": "New Delhi", "to": "HWH", "to_name": "Howrah", "label": "Delhi → Kolkata"},
        {"from": "NDLS", "from_name": "New Delhi", "to": "MAS", "to_name": "Chennai Central", "label": "Delhi → Chennai"},
        {"from": "NDLS", "from_name": "New Delhi", "to": "PNBE", "to_name": "Patna Jn", "label": "Delhi → Patna"},
        {"from": "BCT", "from_name": "Mumbai Central", "to": "SBC", "to_name": "Bangalore City", "label": "Mumbai → Bangalore"},
        {"from": "HWH", "from_name": "Howrah", "to": "MAS", "to_name": "Chennai Central", "label": "Kolkata → Chennai"},
        {"from": "NDLS", "from_name": "New Delhi", "to": "KOTA", "to_name": "Kota Jn", "label": "Delhi → Kota"},
        {"from": "KOTA", "from_name": "Kota Jn", "to": "PNBE", "to_name": "Patna Jn", "label": "Kota → Patna"},
    ]
    return Response({'popular_routes': routes})
