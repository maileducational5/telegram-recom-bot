import requests
import random
from config import OMDB_API_KEY, TMDB_API_KEY


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

    return requests.get(url, params=params).json()


# ---------------------------
# TMDB GENRE RECOMMENDATION
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
        "page": random.randint(1, 50)
    }

    res = requests.get(url, params=params).json()

    movies = []

    for m in res.get("results", []):
        if m.get("vote_average", 0) > 6.5 and m.get("vote_count", 0) > 200:
            movies.append({
                "title": m["title"],
                "rating": m["vote_average"],
                "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
            })

    random.shuffle(movies)

    return movies[:5]


# ---------------------------
# TMDB SIMILAR MOVIES
# ---------------------------
import requests

def get_tmdb_id(title):
    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        # Raise error for bad status (4xx, 5xx)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if results:
            return results[0].get("id")

    except requests.exceptions.RequestException as e:
        print(f"[TMDB ERROR] {e}")

    except ValueError:
        print("[TMDB ERROR] Invalid JSON response")

    return None


def get_similar_movies(title):
    movie_id = get_tmdb_id(title)

    if not movie_id:
        return []

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"

    params = {"api_key": TMDB_API_KEY}

    res = requests.get(url, params=params).json()

    movies = []

    for m in res.get("results", []):
        movies.append({
            "title": m["title"],
            "rating": m["vote_average"],
            "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
        })

    return movies[:5]


# ---------------------------
# SMART ENGINE
# ---------------------------
def smart_recommendation(user_id, title, genre):
    similar = get_similar_movies(title)
    genre_movies = get_recommendations(genre)

    combined = similar + genre_movies

    # remove duplicates
    seen = set()
    result = []

    for m in combined:
        if m["title"] not in seen:
            seen.add(m["title"])
            result.append(m)

    return result[:5]