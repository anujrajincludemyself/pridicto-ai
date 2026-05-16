"""
Cache Service using Upstash Redis REST API.
Falls back to in-memory cache if Upstash not configured.
"""
import json
import logging
import requests
import time
from django.conf import settings

logger = logging.getLogger(__name__)

# In-memory fallback cache
_memory_cache = {}


def _upstash_headers():
    return {
        "Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}",
        "Content-Type": "application/json",
    }


def get_cached(key: str):
    """Get a value from cache. Returns None if not found or expired."""
    if not settings.UPSTASH_REDIS_REST_URL:
        # Memory cache fallback
        item = _memory_cache.get(key)
        if item and item['expires'] > time.time():
            return item['value']
        return None

    try:
        url = f"{settings.UPSTASH_REDIS_REST_URL}/get/{key}"
        resp = requests.get(url, headers=_upstash_headers(), timeout=3)
        data = resp.json()
        result = data.get('result')
        if result:
            return json.loads(result)
        return None
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return None


def set_cached(key: str, value, ttl_seconds: int = 3600):
    """Store a value in cache with TTL."""
    if not settings.UPSTASH_REDIS_REST_URL:
        # Memory cache fallback
        _memory_cache[key] = {
            'value': value,
            'expires': time.time() + ttl_seconds,
        }
        return True

    try:
        url = f"{settings.UPSTASH_REDIS_REST_URL}/set/{key}"
        payload = {"value": json.dumps(value), "ex": ttl_seconds}
        resp = requests.post(url, headers=_upstash_headers(), json=payload, timeout=3)
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
        return False


def delete_cached(key: str):
    """Delete a key from cache."""
    if not settings.UPSTASH_REDIS_REST_URL:
        _memory_cache.pop(key, None)
        return True

    try:
        url = f"{settings.UPSTASH_REDIS_REST_URL}/del/{key}"
        requests.post(url, headers=_upstash_headers(), timeout=3)
        return True
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")
        return False
