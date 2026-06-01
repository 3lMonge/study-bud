import streamlit as st

from services.vector_db_service import (
    search_vector_db,
    get_database_count
)


def render_test_page():
    st.title("Test Semantic Retrieval")

    st.write(
        """
        This page tests whether the vector database can retrieve relevant chunks
        from the selected study documents.
        """
    )

    selected_documents = st.session_state.get("selected_documents", [])

    if get_database_count() == 0:
        st.error("The vector database is empty. Upload a PDF first.")
        return

    if not selected_documents:
        st.warning(
            "No documents selected. Go to the Select tab and choose at least one document."
        )
        return

    st.success(
        "Testing retrieval from: " + ", ".join(selected_documents)
    )

    query = st.text_input("Enter a search query")

    n_results = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=5
    )

    if st.button("Search Vector DB"):
        if not query.strip():
            st.warning("Please enter a search query.")
            return

        results = search_vector_db(
            query=query,
            n_results=n_results,
            selected_documents=selected_documents
        )

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
