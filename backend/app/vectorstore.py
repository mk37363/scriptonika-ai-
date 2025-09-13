# backend/app/vectorstore.py
from typing import Dict, List, Tuple
import numpy as np
import faiss

class FaissStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # inner product == cosine при нормализации
        self.texts: List[str] = []

    def _normalize(self, x: np.ndarray) -> np.ndarray:
        # x: (n, d)
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return x / norms

    def add(self, vectors: np.ndarray, raw_texts: List[str]) -> List[int]:
        assert vectors.shape[1] == self.dim
        nv = self._normalize(vectors.astype("float32"))
        self.index.add(nv)
        start = len(self.texts)
        self.texts.extend(raw_texts)
        return list(range(start, start + len(raw_texts)))

    def search(self, query_vec: np.ndarray, k: int) -> Tuple[List[int], List[float]]:
        q = self._normalize(query_vec.astype("float32"))
        D, I = self.index.search(q, k)  # cosine = inner product (после нормализации)
        return I[0].tolist(), D[0].tolist()

# несколько индексов по имени
stores: Dict[str, FaissStore] = {}
def get_or_create(name: str, dim: int) -> FaissStore:
    if name not in stores:
        stores[name] = FaissStore(dim=dim)
    return stores[name]
