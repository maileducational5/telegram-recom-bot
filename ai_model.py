import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load dataset
df = pd.read_csv("tmdb_5000_movies.csv")

# Clean data
df['combined'] = df['title'] + " " + df['overview']
texts = df['combined'].fillna("")

# Load BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Encoding movies... (first time takes time)")

# Convert text → embeddings
embeddings = model.encode(texts.tolist(), show_progress_bar=True)

# Save embeddings
np.save("embeddings.npy", embeddings)

# Save titles
with open("titles.pkl", "wb") as f:
    pickle.dump(df['title'].tolist(), f)

print("✅ Model ready!")