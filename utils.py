import requests
import random
import time
from config import OMDB_API_KEY, TMDB_API_KEY
from cache import get_cache, set_cache
from ai_recommender import recommend as ai_recommend

# ---------------------------
# 🔥 GLOBAL SESSION (FASTER + STABLE)
# ---------------------------
session = requests.Session()


# ---------------------------
# 🔥 SAFE REQUEST WITH RETRY + CACHE
# ---------------------------
def safe_request(url, params, retries=3, delay=1):
    cache_key = f"{url}-{str(params)}"
    cached = get_cache(cache_key)

    if cached:
        return cached

    for attempt in range(retries):
        try:
            res = session.get(url, params=params, timeout=5)

            if res.status_code == 200:
                data = res.json()
                set_cache(cache_key, data)
                return data

            elif res.status_code == 429:
                print("⚠️ Rate limited. Sleeping...")
                time.sleep(2)

        except Exception as e:
            print(f"REQUEST ERROR (Attempt {attempt+1}):", e)
            time.sleep(delay)

    return None


# ---------------------------
# OMDB SEARCH
# ---------------------------
def search_movie(title):
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "plot": "full"
    }

    return safe_request(url, params) or {}


# ---------------------------
# TMDB GENRE DISCOVERY
# ---------------------------
def get_recommendations(genre):
    url = "https://api.themoviedb.org/3/discover/movie"

    genre_ids = {
        "Action": 28,
        "Adventure": 12,
        "Sci-Fi": 878,
        "Drama": 18,
        "Comedy": 35,
        "Horror": 27
    }

    gid = genre_ids.get(genre)
    if not gid:
        return []

    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": gid,
        "page": random.randint(1, 20)
    }

    data = safe_request(url, params)
    if not data:
        return []

    movies = []
    for m in data.get("results", []):
        if m.get("vote_count", 0) > 200:
            movies.append({
                "title": m["title"],
                "rating": m["vote_average"],
                "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
            })

    random.shuffle(movies)
    return movies[:5]


# ---------------------------
# TMDB SEARCH → ID
# ---------------------------
def get_tmdb_id(title):
    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }

    data = safe_request(url, params)
    if not data:
        return None

    results = data.get("results", [])
    return results[0]["id"] if results else None


# ---------------------------
# TMDB SIMILAR
# ---------------------------
def get_similar_movies(title):
    movie_id = get_tmdb_id(title)
    if not movie_id:
        return []

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"
    params = {"api_key": TMDB_API_KEY}

    data = safe_request(url, params)
    if not data:
        return []

    movies = []
    for m in data.get("results", []):
        movies.append({
            "title": m["title"],
            "rating": m["vote_average"],
            "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
        })

    return movies[:5]


# ---------------------------
# ENRICH AI MOVIES
# ---------------------------
def enrich_movie(title):
    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }

    data = safe_request(url, params)
    if not data:
        return None

    results = data.get("results", [])
    if results:
        m = results[0]
        return {
            "title": m["title"],
            "rating": m["vote_average"],
            "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
        }

    return None


# ---------------------------
# 🔥 FINAL HYBRID ENGINE
# ---------------------------
def smart_recommendation(user_id, title, genre):

    # 1. AI (BERT)
    try:
        ai_titles = ai_recommend(title)
    except Exception as e:
        print("AI ERROR:", e)
        ai_titles = []

    ai_movies = []
    for t in ai_titles:
        enriched = enrich_movie(t)
        if enriched:
            ai_movies.append(enriched)

    # 2. TMDB
    genre_movies = get_recommendations(genre)
    similar_movies = get_similar_movies(title)

    # 3. Merge
    combined = ai_movies + similar_movies + genre_movies

    # 4. Remove duplicates
    seen = set()
    result = []

    for m in combined:
        if m["title"] not in seen:
            seen.add(m["title"])
            result.append(m)

    return result[:5]