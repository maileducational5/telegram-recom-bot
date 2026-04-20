import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load saved data
embeddings = np.load("embeddings.npy")

with open("titles.pkl", "rb") as f:
    titles = pickle.load(f)

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')


# def recommend(movie_name, top_n=5):
#     if movie_name not in titles:
#         return []

#     idx = titles.index(movie_name)

#     query_embedding = embeddings[idx].reshape(1, -1)

#     similarity = cosine_similarity(query_embedding, embeddings)[0]

#     # Get top similar indices
#     top_indices = similarity.argsort()[::-1][1:top_n+1]

#     results = [titles[i] for i in top_indices]

#     return results

def recommend(movie_name, top_n=5):
    query_embedding = model.encode([movie_name])

    similarity = cosine_similarity(query_embedding, embeddings)[0]

    top_indices = similarity.argsort()[::-1][:top_n]

    return [titles[i] for i in top_indices]