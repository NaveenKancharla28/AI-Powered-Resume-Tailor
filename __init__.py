from ingest import load_data_to_faiss, process_pdfs, process_csvs
from chunking import chunk_pdf_data, chunk_csv_data
from embeddings import generate_embeddings_for_chunks
from retrieval import FAISSVectorStore

# Initialize FAISS store
faiss_store = None


def setup_rag_system():
    """Set up the retrieval system from career evidence in the data directory."""
    global faiss_store
    print("Setting up the RAG system...")
    data_directory = "data"
    faiss_store = load_data_to_faiss(data_directory)


def retrieve_answer(question, k=5, filters=None):
    """Retrieve career evidence using hybrid semantic + lexical search."""
    if faiss_store is None:
        print("Error: FAISS store not initialized. Call setup_rag_system() first.")
        return None

    print(f"Processing query: {question}")
    query_chunks = chunk_pdf_data({"query": question})
    query_embeddings = generate_embeddings_for_chunks(query_chunks)
    query_embedding = query_embeddings["query"][0]["embedding"]
    return faiss_store.search(
        query_embedding,
        query_text=question,
        k=k,
        filters=filters,
    )
