def chunk_text(text, chunk_size=200):
    """
    Splits text into smaller chunks of approximately `chunk_size` words.
    """
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])


def chunk_pdf_data(pdf_data, chunk_size=200):
    """
    Chunk PDF data into smaller chunks.
    """
    chunked_data = {}
    for filename, text in pdf_data.items():
        chunks = list(chunk_text(text, chunk_size))
        if not chunks:
            print(f"No chunks generated for {filename}.")
        chunked_data[filename] = chunks
    return chunked_data


def chunk_csv_data(csv_data, group_by=None):
    """
    Chunk CSV data.
    - If `group_by` is provided, group rows by the specified column.
    """
    chunked_data = {}
    for filename, rows in csv_data.items():
        if group_by:
            # Group rows by the specified column
            grouped_chunks = {}
            for row in rows:
                key = row.get(group_by, "Ungrouped")
                grouped_chunks.setdefault(key, []).append(row)
            if not grouped_chunks:
                print(f"No chunks generated for {filename}.")
            chunked_data[filename] = grouped_chunks
        else:
            # Treat each row as a chunk
            if not rows:
                print(f"No chunks generated for {filename}.")
            chunked_data[filename] = rows
    return chunked_data

