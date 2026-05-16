"""
Pridicto Graph Engine - BFS Route Finder
Trains as edges, stations as nodes.
Finds all routes between origin and destination with up to maxHops connections.
"""
from collections import defaultdict, deque
from datetime import datetime, timedelta
import re


def parse_time(time_str):
    """Parse HH:MM format to minutes since midnight."""
    if not time_str or time_str == '--':
        return None
    try:
        parts = time_str.strip().split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return None


def minutes_to_hhmm(minutes):
    """Convert minutes since midnight to HH:MM string."""
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def time_diff_minutes(departure, arrival):
    """
    Compute minutes from arrival to departure across midnight if needed.
    Returns positive integer representing wait time.
    """
    diff = departure - arrival
    if diff < 0:
        diff += 24 * 60  # cross midnight
    return diff


def build_graph(train_schedules):
    """
    Build adjacency graph from train schedules.
    
    train_schedules: list of dicts, each with:
      {
        "train_no": "12001",
        "train_name": "Shatabdi Express",
        "stops": [
          {"station_code": "NDLS", "station_name": "New Delhi", "departure": "06:00", "arrival": "00:00", "day": 1},
          {"station_code": "AGC",  "station_name": "Agra Cantt",  "departure": "08:00", "arrival": "07:58", "day": 1},
          ...
        ]
      }
    
    Returns graph: { station_code: [ {to, train_no, train_name, departure, arrival, duration_min} ] }
    """
    graph = defaultdict(list)

    for train in train_schedules:
        stops = train.get('stops', [])
        for i in range(len(stops)):
            for j in range(i + 1, len(stops)):
                src = stops[i]
                dst = stops[j]

                dep_min = parse_time(src.get('departure'))
                arr_min = parse_time(dst.get('arrival'))

                if dep_min is None or arr_min is None:
                    continue

                # Account for day difference
                day_diff = dst.get('day', 1) - src.get('day', 1)
                duration = arr_min - dep_min + day_diff * 24 * 60
                if duration <= 0:
                    duration += 24 * 60

                graph[src['station_code']].append({
                    'to': dst['station_code'],
                    'to_name': dst.get('station_name', dst['station_code']),
                    'from_name': src.get('station_name', src['station_code']),
                    'train_no': train['train_no'],
                    'train_name': train.get('train_name', ''),
                    'departure': src['departure'],
                    'arrival': dst['arrival'],
                    'departure_min': dep_min,
                    'arrival_min': arr_min + day_diff * 24 * 60,
                    'duration_min': duration,
                    'classes': train.get('classes', ['SL', '3A', '2A', '1A']),
                    'day': src.get('day', 1),
                })

    return graph


def is_connection_valid(prev_edge, next_edge, min_wait_min=30, max_wait_min=300):
    """Check if connection between two train legs is time-feasible."""
    arrival = prev_edge['arrival_min']
    departure = next_edge['departure_min']
    wait = time_diff_minutes(departure, arrival)
    return min_wait_min <= wait <= max_wait_min


def score_route(route):
    """
    Score a route. Lower is better.
    Score = total journey time + (wait penalty per connection * 0.5)
    """
    if not route:
        return float('inf')

    total_journey = 0
    total_wait = 0

    for i, leg in enumerate(route):
        total_journey += leg['duration_min']
        if i > 0:
            wait = time_diff_minutes(leg['departure_min'], route[i - 1]['arrival_min'])
            total_wait += wait

    return total_journey + total_wait * 0.5


def bfs_all_paths(graph, origin, destination, max_hops=2, max_results=10):
    """
    BFS to find all routes from origin to destination with at most max_hops connections.
    
    Returns list of routes, each route = list of edge dicts (legs of journey).
    """
    results = []

    # Queue item: (current_station, path_so_far, visited_stations, last_edge)
    queue = deque()
    queue.append((origin, [], set([origin]), None))

    while queue and len(results) < max_results * 3:
        current, path, visited, last_edge = queue.popleft()

        if current == destination and path:
            results.append(path)
            continue

        if len(path) >= max_hops:
            continue

        for edge in graph.get(current, []):
            next_station = edge['to']

            if next_station in visited:
                continue

            # If this is a connecting train (not the first leg), validate connection time
            if last_edge is not None:
                # Must be a different train
                if edge['train_no'] == last_edge['train_no']:
                    continue  # same train, handled as single leg
                if not is_connection_valid(last_edge, edge):
                    continue

            new_visited = visited | {next_station}
            new_path = path + [edge]
            queue.append((next_station, new_path, new_visited, edge))

    return results


def find_routes(train_schedules, origin, destination, max_hops=2, max_results=5):
    """
    Main entry point for route finding.
    
    Returns sorted list of route objects ready for API response.
    """
    graph = build_graph(train_schedules)
    paths = bfs_all_paths(graph, origin, destination, max_hops=max_hops)

    scored = []
    for path in paths:
        score = score_route(path)
        total_duration = sum(leg['duration_min'] for leg in path)
        total_wait = sum(
            time_diff_minutes(path[i]['departure_min'], path[i - 1]['arrival_min'])
            for i in range(1, len(path))
        )
        num_changes = len(path) - 1

        scored.append({
            'score': score,
            'legs': path,
            'num_changes': num_changes,
            'total_duration_min': total_duration,
            'total_wait_min': total_wait,
            'total_duration_human': f"{total_duration // 60}h {total_duration % 60}m",
            'trains': list({leg['train_no'] for leg in path}),
        })

    scored.sort(key=lambda x: x['score'])
    return scored[:max_results]


# ─── Fallback Mock Data (used when API key is not set) ─────────────────────────

MOCK_TRAINS = [
    {
        "train_no": "12001",
        "train_name": "Shatabdi Express",
        "classes": ["CC", "EC"],
        "stops": [
            {"station_code": "NDLS", "station_name": "New Delhi", "departure": "06:00", "arrival": "00:00", "day": 1},
            {"station_code": "AGC",  "station_name": "Agra Cantt",  "departure": "08:05", "arrival": "07:58", "day": 1},
            {"station_code": "KOTA", "station_name": "Kota Jn",     "departure": "11:40", "arrival": "11:35", "day": 1},
        ],
    },
    {
        "train_no": "12953",
        "train_name": "August Kranti Rajdhani",
        "classes": ["SL", "3A", "2A", "1A"],
        "stops": [
            {"station_code": "NDLS", "station_name": "New Delhi",  "departure": "17:35", "arrival": "00:00", "day": 1},
            {"station_code": "KOTA", "station_name": "Kota Jn",    "departure": "22:05", "arrival": "22:00", "day": 1},
            {"station_code": "BRC",  "station_name": "Vadodara",   "departure": "02:35", "arrival": "02:25", "day": 2},
            {"station_code": "BCT",  "station_name": "Mumbai Central", "departure": "08:15", "arrival": "08:15", "day": 2},
        ],
    },
    {
        "train_no": "12302",
        "train_name": "Howrah Rajdhani",
        "classes": ["SL", "3A", "2A", "1A"],
        "stops": [
            {"station_code": "NDLS", "station_name": "New Delhi",  "departure": "16:55", "arrival": "00:00", "day": 1},
            {"station_code": "CNB",  "station_name": "Kanpur Central", "departure": "20:50", "arrival": "20:45", "day": 1},
            {"station_code": "ALD",  "station_name": "Prayagraj",  "departure": "22:40", "arrival": "22:30", "day": 1},
            {"station_code": "MGS",  "station_name": "Mughal Sarai", "departure": "00:25", "arrival": "00:15", "day": 2},
            {"station_code": "PNBE", "station_name": "Patna",      "departure": "03:45", "arrival": "03:40", "day": 2},
            {"station_code": "HWH",  "station_name": "Howrah",     "departure": "10:00", "arrival": "10:00", "day": 2},
        ],
    },
    {
        "train_no": "12381",
        "train_name": "Poorva Express",
        "classes": ["SL", "3A", "2A"],
        "stops": [
            {"station_code": "HWH",  "station_name": "Howrah",       "departure": "08:10", "arrival": "00:00", "day": 1},
            {"station_code": "PNBE", "station_name": "Patna",         "departure": "15:35", "arrival": "15:25", "day": 1},
            {"station_code": "MGS",  "station_name": "Mughal Sarai",  "departure": "17:20", "arrival": "17:10", "day": 1},
            {"station_code": "ALD",  "station_name": "Prayagraj",     "departure": "19:05", "arrival": "18:50", "day": 1},
            {"station_code": "CNB",  "station_name": "Kanpur Central","departure": "21:25", "arrival": "21:10", "day": 1},
            {"station_code": "NDLS", "station_name": "New Delhi",     "departure": "06:00", "arrival": "06:00", "day": 2},
        ],
    },
    {
        "train_no": "11452",
        "train_name": "Shram Shakti Express",
        "classes": ["SL", "3A", "2A"],
        "stops": [
            {"station_code": "KOTA", "station_name": "Kota Jn",      "departure": "21:10", "arrival": "00:00", "day": 1},
            {"station_code": "CNB",  "station_name": "Kanpur Central","departure": "03:55", "arrival": "03:45", "day": 2},
            {"station_code": "PNBE", "station_name": "Patna",         "departure": "13:00", "arrival": "12:50", "day": 2},
        ],
    },
]
