"""
Groq AI Service - Natural language train search using LLaMA 3 (free via Groq).
Much faster than Claude and completely free with your API key.
Model: llama3-70b-8192
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Pridicto, an intelligent Indian Railways assistant.
Help users find the best train routes across India.

When parsing queries, extract:
- origin: station code or name (e.g. NDLS, "New Delhi")
- destination: station code or name
- date: YYYYMMDD format (today if not specified)
- preferences: special requirements

When formatting results, be friendly, concise, highlight:
- Train names/numbers, departure/arrival times, journey duration
- Best value and fastest options
Always respond helpfully. Use 12-hour time format. Currency in ₹."""


def _get_groq_client():
    try:
        from groq import Groq
        return Groq(api_key=settings.GROQ_API_KEY)
    except ImportError:
        logger.error("groq package not installed. Run: pip install groq")
        return None


def parse_search_intent(user_query: str) -> dict:
    """
    Use Groq LLaMA 3 to parse natural language into structured search data.
    Returns dict with origin, destination, date, preferences.
    """
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — using simple parser")
        return _simple_intent_parser(user_query)

    client = _get_groq_client()
    if not client:
        return _simple_intent_parser(user_query)

    try:
        chat = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=512,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"""Parse this train search query and return ONLY a JSON object (no markdown, no explanation):

Query: "{user_query}"

Return format:
{{
  "origin": "station code or name",
  "destination": "station code or name",
  "date": "YYYYMMDD or null",
  "preferences": ["list", "of", "preferences"],
  "is_valid": true,
  "error": null
}}"""
                }
            ]
        )

        response_text = chat.choices[0].message.content.strip()
        # Strip any markdown fences
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        return json.loads(response_text)

    except json.JSONDecodeError as e:
        logger.error(f"Groq JSON parse error: {e}")
        return _simple_intent_parser(user_query)
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return _simple_intent_parser(user_query)


def format_routes_with_ai(routes: list, query: str) -> str:
    """
    Use Groq LLaMA 3 to generate a human-readable route summary.
    """
    if not settings.GROQ_API_KEY or not routes:
        return _simple_format_routes(routes)

    client = _get_groq_client()
    if not client:
        return _simple_format_routes(routes)

    try:
        routes_json = json.dumps(routes[:3], indent=2)

        chat = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=600,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"""User asked: "{query}"

Top routes found:
{routes_json}

Write a friendly 2-3 sentence summary recommending the best route.
Mention fastest option and most comfortable if they differ. Be concise and practical."""
                }
            ]
        )

        return chat.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Groq format error: {e}")
        return _simple_format_routes(routes)


def _simple_intent_parser(query: str) -> dict:
    """Simple regex fallback when Groq is not available."""
    import re
    from datetime import datetime

    query_lower = query.lower()

    station_map = {
        'delhi': 'NDLS', 'new delhi': 'NDLS',
        'mumbai': 'BCT', 'bombay': 'BCT',
        'kolkata': 'HWH', 'calcutta': 'HWH', 'howrah': 'HWH',
        'patna': 'PNBE', 'kota': 'KOTA',
        'agra': 'AGC', 'kanpur': 'CNB',
        'prayagraj': 'ALD', 'allahabad': 'ALD',
        'vadodara': 'BRC', 'baroda': 'BRC',
        'jaipur': 'JP', 'chennai': 'MAS',
        'bangalore': 'SBC', 'bengaluru': 'SBC',
        'hyderabad': 'SC', 'pune': 'PUNE',
        'ahmedabad': 'ADI',
    }

    patterns = [
        r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+on|\s+for|\s*$)',
        r'([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+on|\s+for|\s*$)',
    ]

    origin, destination = None, None
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            o = match.group(1).strip()
            d = match.group(2).strip()
            origin = station_map.get(o, o.upper().replace(' ', ''))
            destination = station_map.get(d, d.upper().replace(' ', ''))
            break

    return {
        "origin": origin,
        "destination": destination,
        "date": datetime.now().strftime('%Y%m%d'),
        "preferences": [],
        "is_valid": bool(origin and destination),
        "error": None if (origin and destination) else "Could not parse origin/destination from query.",
    }


def _simple_format_routes(routes: list) -> str:
    if not routes:
        return "No routes found. Try different stations or check if the train data API is configured."

    best = routes[0]
    legs = best['legs']

    if len(legs) == 1:
        leg = legs[0]
        return (
            f"✅ Best route: {leg['train_name']} ({leg['train_no']}) "
            f"departing at {leg['departure']}, arriving at {leg['arrival']}. "
            f"Journey time: {best['total_duration_human']}."
        )
    else:
        trains = " → ".join([f"{l['train_name']} ({l['train_no']})" for l in legs])
        return (
            f"✅ Best route with {best['num_changes']} change(s): {trains}. "
            f"Total journey: {best['total_duration_human']} "
            f"(including {best['total_wait_min']} min wait at connection)."
        )
