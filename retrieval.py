import faiss
import numpy as np

class FAISSVectorStore:
    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata = []

    def add_embeddings(self, embeddings, metadata):
        if len(embeddings) == 0:
            print("No embeddings to add.")
            return

        embeddings_np = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings_np)
        self.metadata.extend(metadata)
        print(f"FAISS index now contains {self.index.ntotal} embeddings.")

    def search(self, query_embedding, k=5):
        if self.index.ntotal == 0:
            print("FAISS index is empty. No results to return.")
            return []

        query_embedding_np = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_embedding_np, k)

        results = []
        for j, i in enumerate(indices[0]):
            if i != -1 and i < len(self.metadata):
                chunk_text = self.metadata[i]["chunk"]
                clean_chunk = ''.join(c for c in chunk_text if c.isprintable())  # Remove weird characters
                
                results.append({
                    "filename": self.metadata[i]["filename"],
                    "chunk": clean_chunk,
                    "distance": distances[0][j]
                })

        return results  # Don't print results here! It should be printed in `app.py`
