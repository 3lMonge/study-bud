import streamlit as st

from services.pdf_service import (
    save_uploaded_pdf,
    extract_text_from_pdf,
    delete_temp_file
)

from services.vector_db_service import (
    store_pdf_pages,
    search_vector_db,
    get_database_count
)


def render_upload_page():
    st.header("Upload PDF")

    st.write(
        """
        Upload a PDF to test the document ingestion pipeline.
        The app will extract text, split it into chunks, create embeddings,
        and store everything in ChromaDB.
        """
    )

    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:
        st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("Extract and Store in Vector DB"):
            temp_pdf_path = None

            with st.spinner("Processing PDF..."):
                try:
                    temp_pdf_path = save_uploaded_pdf(uploaded_file)
                    pages = extract_text_from_pdf(temp_pdf_path)

                    if not pages:
                        st.error("No readable text was found in this PDF.")
                        return

                    stored_count = store_pdf_pages(
                        filename=uploaded_file.name,
                        pages=pages
                    )

                    st.success(
                        f"Done. Stored {stored_count} chunks from {len(pages)} pages."
                    )

                    with st.expander("Preview extracted text"):
                        for page in pages[:3]:
                            st.subheader(f"Page {page['page']}")
                            st.write(page["text"][:1500])

                finally:
                    delete_temp_file(temp_pdf_path)


def render_database_status_page():
    st.header("Database Status")

    count = get_database_count()

    st.metric("Total Stored Chunks", count)

    if count > 0:
        st.success("The vector database has stored content.")
    else:
        st.warning("The vector database is empty.")

    st.write("Each stored item includes:")

    st.code(
        """
Text chunk
Embedding vector
Metadata:
  - filename
  - page number
  - chunk index
        """
    )


def render_test_search_page():
    st.header("Test Search")

    st.write(
        """
        Use this page to confirm that the uploaded PDF content
        can be retrieved from the vector database.
        """
    )

    query = st.text_input("Search the vector database")

    n_results = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=5
    )

    if st.button("Search"):
        if not query.strip():
            st.warning("Please enter a search query.")
            return

        if get_database_count() == 0:
            st.error("The vector database is empty. Upload a PDF first.")
            return

        results = search_vector_db(query, n_results=n_results)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            st.warning("No results found.")
            return

        st.success(f"Found {len(documents)} result(s).")

        for i, document in enumerate(documents):
            metadata = metadatas[i]
            distance = distances[i] if distances else None

            title = (
                f"Result {i + 1} — "
                f"{metadata['filename']} | "
                f"Page {metadata['page']}"
            )

            with st.expander(title):
                st.write(document)
                st.caption(
                    f"Chunk index: {metadata['chunk_index']} | Distance: {distance}"
                )
