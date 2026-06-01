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


def build_document_filter(selected_documents):
    """
    Builds a ChromaDB metadata filter based on selected documents.
    """
    if not selected_documents:
        return None

    if len(selected_documents) == 1:
        return {
            "filename": selected_documents[0]
        }

    return {
        "$or": [
            {"filename": filename}
            for filename in selected_documents
        ]
    }


def search_vector_db(query, n_results=5, selected_documents=None):
    """
    Searches ChromaDB using semantic similarity.

    If selected_documents is provided, the search is limited to those documents.
    """
    collection = get_collection()
    query_embedding = embed_text(query)

    document_filter = build_document_filter(selected_documents)

    if document_filter:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=document_filter
        )
    else:
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


def list_stored_documents():
    """
    Returns a list of unique documents stored in ChromaDB.

    Output:
        [
            {
                "filename": "paper.pdf",
                "chunk_count": 12,
                "page_count": 5
            }
        ]
    """
    collection = get_collection()

    if collection.count() == 0:
        return []

    data = collection.get(
        include=["metadatas"]
    )

    metadatas = data.get("metadatas", [])

    documents = {}

    for metadata in metadatas:
        filename = metadata.get("filename")
        page = metadata.get("page")

        if filename not in documents:
            documents[filename] = {
                "filename": filename,
                "chunk_count": 0,
                "pages": set()
            }

        documents[filename]["chunk_count"] += 1

        if page is not None:
            documents[filename]["pages"].add(page)

    result = []

    for doc in documents.values():
        result.append({
            "filename": doc["filename"],
            "chunk_count": doc["chunk_count"],
            "page_count": len(doc["pages"])
        })

    result.sort(key=lambda x: x["filename"])

    return result


def get_database_info():
    """
    Returns useful database information for the UI.
    """
    documents = list_stored_documents()

    return {
        "db_path": DB_PATH,
        "collection_name": COLLECTION_NAME,
        "stored_chunks": get_database_count(),
        "document_count": len(documents)
    }
