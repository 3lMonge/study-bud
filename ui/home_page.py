import streamlit as st


def render_home_page():
    st.title("Study Agent")

    st.subheader("A document-based study assistant powered by retrieval.")

    st.write(
        """
        This app is an MVP for a study agent that helps students work with academic PDFs.
        The goal is to upload course documents, store them in a vector database,
        select which documents to study, and eventually chat with an LLM that answers
        using only the selected sources.
        """
    )

    st.markdown("### Current MVP Features")

    st.write(
        """
        Right now, the app can:
        """
    )

    st.markdown(
        """
        - Upload PDF files
        - Extract text from each page
        - Split extracted text into smaller chunks
        - Create embeddings for each chunk
        - Store chunks in a local ChromaDB vector database
        - Show which documents are stored
        - Let the user select documents for study
        - Test semantic retrieval from the vector database
        - Use a temporary chat interface that retrieves relevant chunks
        """
    )

    st.markdown("### Development Flow")

    st.code(
        """
Upload PDF
↓
Extract text
↓
Chunk text
↓
Embed chunks
↓
Store in ChromaDB
↓
Select study documents
↓
Retrieve relevant chunks
↓
Future step: send retrieved chunks to an LLM
        """
    )

    st.info(
        "The LLM answer generation step is not connected yet. "
        "The current version is focused on testing document ingestion and retrieval."
    )
