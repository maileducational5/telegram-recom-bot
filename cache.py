#cache.py

import time

cache = {}

def get_cache(key, expiry=3600):
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < expiry:
            return data
    return None

def set_cache(key, data):
    cache[key] = (data, time.time())