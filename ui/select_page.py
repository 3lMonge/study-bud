import streamlit as st

from services.vector_db_service import list_stored_documents


def render_select_page():
    st.title("Select Study Documents")

    st.write(
        """
        Select which stored documents the study agent should use.
        The chat and retrieval test will focus on the selected documents.
        """
    )

    documents = list_stored_documents()

    if not documents:
        st.warning("No documents are stored yet. Upload a PDF first.")
        return

    document_names = [doc["filename"] for doc in documents]

    selected_documents = st.multiselect(
        "Choose one or more documents for study",
        options=document_names,
        default=st.session_state.get("selected_documents", [])
    )

    st.session_state.selected_documents = selected_documents

    if selected_documents:
        st.success(f"{len(selected_documents)} document(s) selected.")

        st.markdown("### Selected Documents")

        for doc_name in selected_documents:
            doc_info = next(
                doc for doc in documents if doc["filename"] == doc_name
            )

            st.write(
                f"**{doc_info['filename']}** — "
                f"{doc_info['chunk_count']} chunks"
            )

    else:
        st.info("No documents selected yet.")

    st.markdown("### Documents in Vector DB")

    for doc in documents:
        with st.expander(doc["filename"]):
            st.write(f"Stored chunks: {doc['chunk_count']}")
            st.write(f"Pages detected: {doc['page_count']}")
