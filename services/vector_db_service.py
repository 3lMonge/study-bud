import chromadb
import hashlib
import streamlit as st

from services.chunking_service import chunk_text
from services.embedding_service import embed_text


DB_PATH = "./chroma_db"
COLLECTION_NAME = "study_documents"


@st.cache_resource
def get_collection():
    """
    Connects to a persistent ChromaDB collection.
    """
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def create_document_id(filename, page_number, chunk_index, chunk):
    """
    Creates a stable unique ID for each text chunk.
    """
    raw_id = f"{filename}-{page_number}-{chunk_index}-{chunk[:80]}"
    return hashlib.md5(raw_id.encode()).hexdigest()


def store_pdf_pages(filename, pages):
    """
    Chunks, embeds, and stores PDF text in ChromaDB.
    """
    collection = get_collection()
    stored_count = 0

    for page in pages:
        page_number = page["page"]
        text = page["text"]

        chunks = chunk_text(text)

        for chunk_index, chunk in enumerate(chunks):
            doc_id = create_document_id(
                filename=filename,
                page_number=page_number,
                chunk_index=chunk_index,
                chunk=chunk
            )

            embedding = embed_text(chunk)

            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "filename": filename,
                    "page": page_number,
                    "chunk_index": chunk_index
                }]
            )

            stored_count += 1

    return stored_count


def search_vector_db(query, n_results=5):
    """
    Searches ChromaDB using semantic similarity.
    """
    collection = get_collection()
    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


def get_database_count():
    """
    Returns the total number of stored chunks.
    """
    collection = get_collection()
    return collection.count()


def get_database_info():
    """
    Returns useful database information for the UI.
    """
    return {
        "db_path": DB_PATH,
        "collection_name": COLLECTION_NAME,
        "stored_chunks": get_database_count()
    }
