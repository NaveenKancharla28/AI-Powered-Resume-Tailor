from ingest import load_data_to_faiss, process_pdfs, process_csvs
from chunking import chunk_pdf_data, chunk_csv_data
from embeddings import generate_embeddings_for_chunks
from retrieval import FAISSVectorStore

# Initialize FAISS store
faiss_store = None

def setup_rag_system():
    """
    Sets up the Retrieval-Augmented Generation (RAG) system.
    """
    global faiss_store
    print("Setting up the RAG system...")
    data_directory = "data"  # Update this if needed
    faiss_store = load_data_to_faiss(data_directory)

def retrieve_answer(question):
    """
    Retrieve relevant answers from the vector database based on a query.
    """
    if faiss_store is None:
        print("Error: FAISS store not initialized. Call setup_rag_system() first.")
        return None
    
    print(f"Processing query: {question}")
    
    # Mock chunking process for the query
    query_chunks = chunk_pdf_data({"query": question})  # Ensure question is a string, not a list
    
    # Generate embeddings for the query
    query_embeddings = generate_embeddings_for_chunks(query_chunks)
    query_embedding = query_embeddings["query"][0]["embedding"]
    
    # Search in FAISS
    results = faiss_store.search(query_embedding, k=5)
    return results
