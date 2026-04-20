import time

cache_store = {}

CACHE_TTL = 60 * 60  # 1 hour


def get_cache(key):
    if key in cache_store:
        data, ts = cache_store[key]
        if time.time() - ts < CACHE_TTL:
            return data
    return None


def set_cache(key, value):
    cache_store[key] = (value, time.time())