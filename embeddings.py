from sentence_transformers import SentenceTransformer

def generate_embeddings_for_chunks(chunked_data):
    """
    Generate embeddings for chunked data using a pre-trained model.
    :param chunked_data: Dictionary with filenames as keys and list of chunks as values.
    :return: Dictionary with filenames as keys and list of embeddings as values.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Use a sentence-transformer model
    embeddings = {}
    for filename, chunks in chunked_data.items():
        # Ensure all chunks are strings
        valid_chunks = [chunk for chunk in chunks if isinstance(chunk, str)]
        embeddings[filename] = [
            {"chunk": chunk, "embedding": model.encode(chunk)} for chunk in valid_chunks
        ]
    return embeddings

