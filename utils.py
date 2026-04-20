#utils.py

import requests
from config import OMDB_API_KEY

def search_movie(title):
    url = "http://www.omdbapi.com/"
    
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "plot": "full"
    }

    response = requests.get(url, params=params)
    return response.json()

from cache import get_cache, set_cache

# def search_movie(title):
#     cached = get_cache(title)
#     if cached:
#         return cached

#     response = requests.get(...)
#     data = response.json()

#     set_cache(title, data)
#     return data

# def detect_type(query):
#     query = query.lower()
#     if "season" in query or "s0" in query:
#         return "series"
#     return "movie"

# def get_recommendations(genre):
#     # simple static example
#     return [
#         "Inception",
#         "Interstellar",
#         "The Dark Knight"
#     ]
    
# user_history = {}

# def track_user(user_id, movie):
#     if user_id not in user_history:
#         user_history[user_id] = []
    
#     user_history[user_id].append(movie)

import re

def clean_query(q):
    return re.sub(r'[^\w\s]', '', q)[:100]