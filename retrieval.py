import math
import re
from collections import Counter

import faiss
import numpy as np


_TOKEN_RE = re.compile(r"[A-Za-z0-9+#.]+")


def _tokens(text):
    return [token.lower() for token in _TOKEN_RE.findall(text or "")]


class BM25Index:
    """Small dependency-free BM25 index for career-evidence chunks."""

    def __init__(self, documents):
        self.documents = documents
        self.doc_tokens = [_tokens(doc.get("chunk", "")) for doc in documents]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avgdl = sum(self.doc_lengths) / max(len(self.doc_lengths), 1)
        self.term_frequency = [Counter(tokens) for tokens in self.doc_tokens]
        self.document_frequency = Counter()
        for tokens in self.doc_tokens:
            self.document_frequency.update(set(tokens))

    def search(self, query, limit=None, filters=None):
        query_tokens = _tokens(query)
        if not query_tokens:
            return []
        k1, b = 1.5, 0.75
        results = []
        filters = filters or {}
        for index, tf in enumerate(self.term_frequency):
            metadata = self.documents[index]
            if not _matches_filters(metadata, filters):
                continue
            score = 0.0
            for token in query_tokens:
                freq = tf.get(token, 0)
                if not freq:
                    continue
                df = self.document_frequency.get(token, 0)
                idf = math.log(1 + (len(self.documents) - df + 0.5) / (df + 0.5))
                denominator = freq + k1 * (1 - b + b * self.doc_lengths[index] / max(self.avgdl, 1))
                score += idf * (freq * (k1 + 1)) / denominator
            if score > 0:
                results.append((index, score))
        results.sort(key=lambda item: item[1], reverse=True)
        return results[:limit] if limit else results


def _matches_filters(metadata, filters):
    for key, expected in filters.items():
        if expected is None:
            continue
        actual = metadata.get(key)
        if isinstance(expected, (list, tuple, set)):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


class FAISSVectorStore:
    """Hybrid vector + BM25 retrieval with deterministic reranking and metadata filters."""

    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata = []
        self.bm25 = BM25Index([])

    def add_embeddings(self, embeddings, metadata):
        if len(embeddings) == 0:
            print("No embeddings to add.")
            return
        embeddings_np = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings_np)
        self.metadata.extend(metadata)
        self.bm25 = BM25Index(self.metadata)
        print(f"FAISS index now contains {self.index.ntotal} embeddings.")

    def _vector_candidates(self, query_embedding, candidate_limit, filters):
        if self.index.ntotal == 0:
            return []
        query_embedding_np = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_embedding_np, min(candidate_limit, self.index.ntotal))
        candidates = []
        for distance, index in zip(distances[0], indices[0]):
            if index == -1 or index >= len(self.metadata):
                continue
            if not _matches_filters(self.metadata[index], filters):
                continue
            candidates.append((int(index), float(distance)))
        return candidates

    def search(self, query_embedding, query_text="", k=5, filters=None, candidate_k=20):
        """Retrieve candidates from FAISS and BM25, then rerank their union."""
        filters = filters or {}
        vector_candidates = self._vector_candidates(query_embedding, candidate_k, filters)
        bm25_candidates = self.bm25.search(query_text, limit=candidate_k, filters=filters)
        candidate_ids = {index for index, _ in vector_candidates} | {index for index, _ in bm25_candidates}

        vector_scores = {index: 1.0 / (1.0 + distance) for index, distance in vector_candidates}
        bm25_scores = {index: score for index, score in bm25_candidates}
        max_bm25 = max(bm25_scores.values(), default=1.0)
        max_vector = max(vector_scores.values(), default=1.0)

        ranked = []
        for index in candidate_ids:
            vector_score = vector_scores.get(index, 0.0) / max_vector
            lexical_score = bm25_scores.get(index, 0.0) / max_bm25
            # Favor semantic similarity while giving exact keyword evidence a strong boost.
            rerank_score = 0.60 * vector_score + 0.40 * lexical_score
            ranked.append((index, rerank_score, vector_score, lexical_score))

        ranked.sort(key=lambda item: item[1], reverse=True)
        results = []
        for index, rerank_score, vector_score, lexical_score in ranked[:k]:
            metadata = self.metadata[index]
            clean_chunk = "".join(c for c in metadata.get("chunk", "") if c.isprintable())
            results.append({
                "filename": metadata.get("filename", ""),
                "chunk": clean_chunk,
                "distance": 1.0 / max(vector_score, 1e-9) - 1.0 if vector_score else None,
                "bm25_score": round(lexical_score, 4),
                "rerank_score": round(rerank_score, 4),
                "metadata": {k: v for k, v in metadata.items() if k != "chunk"},
            })
        return results
