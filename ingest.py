import os
import pandas as pd
from PyPDF2 import PdfReader
from chunking import chunk_pdf_data, chunk_csv_data
from retrieval import FAISSVectorStore
from embeddings import generate_embeddings_for_chunks

def process_pdfs(directory):
    """Extract text from PDF files in the specified directory."""
    pdf_data = {}
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            reader = PdfReader(file_path)
            text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            pdf_data[filename] = text
    return pdf_data

def process_csvs(directory):
    """Extract data from CSV files in the specified directory."""
    csv_data = {}
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            csv_data[filename] = df.to_dict(orient="records")
    return csv_data

def load_data_to_faiss(data_directory):
    """
    Process and chunk PDFs and CSVs, generate embeddings, and store them in FAISS.
    """
    pdfs = process_pdfs(data_directory)
    csvs = process_csvs(data_directory)
    chunked_pdfs = chunk_pdf_data(pdfs)
    chunked_csvs = chunk_csv_data(csvs)

    pdf_embeddings = generate_embeddings_for_chunks(chunked_pdfs)
    csv_embeddings = generate_embeddings_for_chunks(chunked_csvs)

    all_embeddings = [chunk["embedding"] for chunks in pdf_embeddings.values() for chunk in chunks]
    all_embeddings += [chunk["embedding"] for chunks in csv_embeddings.values() for chunk in chunks]

    all_metadata = [{"filename": fn, "chunk": chunk["chunk"]} for fn, chunks in pdf_embeddings.items() for chunk in chunks]
    all_metadata += [{"filename": fn, "chunk": chunk["chunk"]} for fn, chunks in csv_embeddings.items() for chunk in chunks]

    if len(all_embeddings) == 0:
        print("No embeddings generated, FAISS storage skipped.")
        return None

    print(f"Storing {len(all_embeddings)} embeddings in FAISS...")
    
    faiss_store = FAISSVectorStore(len(all_embeddings[0]))
    faiss_store.add_embeddings(all_embeddings, all_metadata)
    
    print(f"Successfully stored {faiss_store.index.ntotal} embeddings in FAISS.")

    return faiss_store

