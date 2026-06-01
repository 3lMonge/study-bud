import streamlit as st

from services.pdf_service import (
    save_uploaded_pdf,
    extract_text_from_pdf,
    delete_temp_file
)

from services.vector_db_service import store_pdf_pages


def render_upload_page():
    st.title("Upload Documents")

    st.write(
        """
        Upload PDF files here. For this MVP, only PDFs are supported.
        The uploaded PDF will be extracted, chunked, embedded, and stored
        in the local ChromaDB vector database.
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
