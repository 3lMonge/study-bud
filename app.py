import streamlit as st
import pymupdf
import chromadb
from sentence_transformers import SentenceTransformer
import tempfile
import os
import hashlib


# -----------------------------
# Basic configuration
# -----------------------------

st.set_page_config(
    page_title="Study Agent PDF Tester",
    page_icon="📄",
    layout="wide"
)

DB_PATH = "./chroma_db"
COLLECTION_NAME = "study_documents"


# -----------------------------
# Load embedding model
# -----------------------------

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


embedding_model = load_embedding_model()


# -----------------------------
# Connect to ChromaDB
# -----------------------------

@st.cache_resource
def get_chroma_collection():
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


collection = get_chroma_collection()


# -----------------------------
# Helper functions
# -----------------------------

def save_uploaded_file(uploaded_file):
    """
    Saves the uploaded PDF temporarily so PyMuPDF can read it.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name


def extract_text_from_pdf(pdf_path):
    """
    Extracts text page by page from the uploaded PDF.
    Returns a list of dictionaries:
    [
        {"page": 1, "text": "..."},
        {"page": 2, "text": "..."}
    ]
    """
    doc = pymupdf.open(pdf_path)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text
            })

    doc.close()
    return pages


def chunk_text(text, chunk_size=800, overlap=150):
    """
    Splits long text into smaller overlapping chunks.
    This helps the vector DB retrieve more precise sections later.
    """
    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_document_id(filename, page_number, chunk_index, chunk_text):
    """
    Creates a unique ID for each stored chunk.
    """
    raw_id = f"{filename}-{page_number}-{chunk_index}-{chunk_text[:50]}"
    return hashlib.md5(raw_id.encode()).hexdigest()


def store_pdf_in_chroma(filename, pages):
    """
    Stores extracted PDF chunks in ChromaDB.
    """
    stored_count = 0

    for page in pages:
        page_number = page["page"]
        text = page["text"]
        chunks = chunk_text(text)

        for chunk_index, chunk in enumerate(chunks):
            embedding = embedding_model.encode(chunk).tolist()

            doc_id = create_document_id(
                filename=filename,
                page_number=page_number,
                chunk_index=chunk_index,
                chunk_text=chunk
            )

            collection.add(
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
    Searches ChromaDB using a query.
    """
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


def get_collection_count():
    """
    Returns how many chunks are currently stored in the vector DB.
    """
    return collection.count()


# -----------------------------
# Streamlit UI
# -----------------------------

st.title("📄 Study Agent PDF Upload + Vector DB Tester")

st.write(
    """
    This is a simple test UI for your agent pipeline.  
    Upload a PDF, extract its text, store it in a local Chroma vector database, 
    and test whether the stored content can be searched.
    """
)

# Sidebar status
st.sidebar.header("Vector DB Status")

current_count = get_collection_count()
st.sidebar.metric("Stored Chunks", current_count)
st.sidebar.write(f"Database path: `{DB_PATH}`")
st.sidebar.write(f"Collection: `{COLLECTION_NAME}`")


# Main layout
tab1, tab2, tab3 = st.tabs([
    "1. Upload PDF",
    "2. View Database Status",
    "3. Test Search"
])


# -----------------------------
# Tab 1: Upload PDF
# -----------------------------

with tab1:
    st.header("Upload and Process PDF")

    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:
        st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("Extract and Store in Vector DB"):
            with st.spinner("Processing PDF..."):
                temp_pdf_path = save_uploaded_file(uploaded_file)

                pages = extract_text_from_pdf(temp_pdf_path)

                if not pages:
                    st.error("No readable text was found in this PDF.")
                else:
                    stored_count = store_pdf_in_chroma(
                        filename=uploaded_file.name,
                        pages=pages
                    )

                    os.remove(temp_pdf_path)

                    st.success(
                        f"Done. Stored {stored_count} chunks from {len(pages)} pages."
                    )

                    st.info(
                        "Go to the 'Test Search' tab and ask a question or search for a phrase from the PDF."
                    )

                    with st.expander("Preview extracted text"):
                        for page in pages[:3]:
                            st.subheader(f"Page {page['page']}")
                            st.write(page["text"][:1500])


# -----------------------------
# Tab 2: DB Status
# -----------------------------

with tab2:
    st.header("Vector Database Status")

    count = get_collection_count()

    st.metric("Total stored chunks", count)

    if count > 0:
        st.success("Your vector database has stored content.")
    else:
        st.warning("Your vector database is empty.")

    st.write(
        """
        Each stored item is a text chunk from the PDF.  
        The vector database stores:
        """
    )

    st.code(
        """
        ID
        Text chunk
        Embedding vector
        Metadata:
          - filename
          - page number
          - chunk index
        """
    )


# -----------------------------
# Tab 3: Search Test
# -----------------------------

with tab3:
    st.header("Search Stored PDF Content")

    query = st.text_input(
        "Enter a question or keyword to search the vector database"
    )

    n_results = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=5
    )

    if st.button("Search Vector DB"):
        if not query.strip():
            st.warning("Please enter a search query.")
        elif get_collection_count() == 0:
            st.error("The vector database is empty. Upload and store a PDF first.")
        else:
            results = search_vector_db(query, n_results=n_results)

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            if not documents:
                st.warning("No results found.")
            else:
                st.success(f"Found {len(documents)} result(s).")

                for i, doc in enumerate(documents):
                    metadata = metadatas[i]
                    distance = distances[i] if distances else None

                    with st.expander(
                        f"Result {i + 1} — {metadata['filename']} | Page {metadata['page']}"
                    ):
                        st.write(doc)

                        st.caption(
                            f"Chunk index: {metadata['chunk_index']} | Distance: {distance}"
                        )
