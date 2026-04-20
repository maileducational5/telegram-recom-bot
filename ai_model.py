import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import json

# ---------------------------
# LOAD DATASET
# ---------------------------
df = pd.read_csv("tmdb_5000_movies.csv")

# ---------------------------
# CLEAN GENRES
# ---------------------------
def extract_genres(x):
    try:
        genres = json.loads(x)
        return " ".join([g['name'] for g in genres])
    except:
        return ""

df['genres_text'] = df['genres'].apply(extract_genres)

# ---------------------------
# COMBINE FEATURES
# ---------------------------
df['combined'] = (
    df['title'].fillna('') + " " +
    df['overview'].fillna('') + " " +
    df['genres_text']
)

texts = df['combined'].fillna('')

# ---------------------------
# LOAD BERT MODEL (CPU SAFE)
# ---------------------------
model = SentenceTransformer(
    'all-MiniLM-L6-v2',
    device='cpu'   # 🔥 avoids CUDA issue
)

print("Encoding movies... (first time takes time)")

# ---------------------------
# CREATE EMBEDDINGS
# ---------------------------
embeddings = model.encode(
    texts.tolist(),
    show_progress_bar=True,
    batch_size=64
)

# ---------------------------
# SAVE FILES
# ---------------------------
np.save("embeddings.npy", embeddings)

with open("titles.pkl", "wb") as f:
    pickle.dump(df['title'].tolist(), f)

print("✅ Model ready!")