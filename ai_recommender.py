#ai_recommender.py
import numpy as np
import random
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------
# LOAD MODEL
# ---------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# ---------------------------
# LOAD PRETRAINED DATA
# ---------------------------
embeddings = np.load("embeddings.npy")

with open("titles.pkl", "rb") as f:
    titles = pickle.load(f)

# ---------------------------
# RECOMMEND FUNCTION
# ---------------------------
def recommend(query_text, top_k=5):
    try:
        # Encode query
        query_vec = model.encode([query_text])

        # Similarity
        scores = cosine_similarity(query_vec, embeddings)[0]

        # Sort indices
        sorted_idx = np.argsort(scores)[::-1]

        # 🔥 Multi-level diversity (VERY IMPORTANT)
        strong = sorted_idx[:10]
        medium = sorted_idx[10:30]
        weak = sorted_idx[30:60]

        picks = []

        if len(strong) >= 2:
            picks += random.sample(list(strong), 2)

        if len(medium) >= 2:
            picks += random.sample(list(medium), 2)

        if len(weak) >= 1:
            picks += random.sample(list(weak), 1)

        random.shuffle(picks)

        results = []

        for i in picks:
            title = titles[i]

            # avoid same movie
            if title.lower() != query_text.lower():
                results.append(title)

            if len(results) >= top_k:
                break

        return results

    except Exception as e:
        print("AI ERROR:", e)
        return []