import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as cos_sim

print("Loading Sentence Transformer: all-MiniLM-L6-v2 ...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model ready.")


def get_embedding(text: str) -> np.ndarray:
    if not text.strip():
        return np.zeros(384)
    return model.encode(text, convert_to_numpy=True)


def compute_similarity(job_text: str, resume_text: str) -> float:
    """
    Returns cosine similarity score in [0, 1].
    1.0 = perfect semantic match, 0.0 = completely unrelated.
    """
    j = get_embedding(job_text).reshape(1, -1)
    r = get_embedding(resume_text).reshape(1, -1)
    score = float(cos_sim(j, r)[0][0])
    return max(0.0, min(1.0, score))
