import streamlit as st

from services.vector_db_service import (
    search_vector_db,
    get_database_count
)

from services.embedding_service import get_embedding_model_name
from services.llm_service import generate_answer, get_llm_model_name


def retrieve_sources(user_question, selected_documents):
    """
    Retrieves relevant chunks from selected documents.
    """

    results = search_vector_db(
        query=user_question,
        n_results=4,
        selected_documents=selected_documents
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    sources = []

    for document, metadata in zip(documents, metadatas):
        sources.append({
            "text": document,
            "filename": metadata["filename"],
            "page": metadata["page"],
            "chunk_index": metadata["chunk_index"]
        })

    return sources


def build_rag_response(user_question, selected_documents):
    """
    Retrieves context from the vector DB and sends it to the local LLM.
    """

    if get_database_count() == 0:
        return {
            "answer": "No documents have been uploaded yet. Please upload a PDF first.",
            "sources": []
        }

    if not selected_documents:
        return {
            "answer": "No documents are selected. Please go to the Select tab and choose a document first.",
            "sources": []
        }

    sources = retrieve_sources(
        user_question=user_question,
        selected_documents=selected_documents
    )

    if not sources:
        return {
            "answer": "I could not find relevant information in the selected documents.",
            "sources": []
        }

    answer = generate_answer(
        question=user_question,
        sources=sources
    )

    return {
        "answer": answer,
        "sources": sources
    }


def render_chat_page():
    st.title("Chat")

    selected_documents = st.session_state.get("selected_documents", [])

    st.markdown("### Model Status")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"LLM Model: **{get_llm_model_name()}**")

    with col2:
        st.info(f"Embedding Model: **{get_embedding_model_name()}**")

    if selected_documents:
        st.success(
            "Selected document(s): " + ", ".join(selected_documents)
        )
    else:
        st.warning(
            "No documents selected. Go to the Select tab before chatting."
        )

    st.markdown("---")

    st.write(
        """
        Ask questions about the selected document(s).
        The app will retrieve relevant chunks from ChromaDB and send them
        to the local Llama model to generate an answer.
        """
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

            if "sources" in message and message["sources"]:
                with st.expander("Retrieved Sources"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**{source['filename']} — Page {source['page']}**"
                        )
                        st.write(source["text"])
                        st.caption(f"Chunk index: {source['chunk_index']}")

    user_question = st.chat_input("Ask something about your selected document(s)...")

    if user_question:
        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking with local Llama model..."):
                response = build_rag_response(
                    user_question=user_question,
                    selected_documents=selected_documents
                )

                st.write(response["answer"])

                if response["sources"]:
                    with st.expander("Retrieved Sources"):
                        for source in response["sources"]:
                            st.markdown(
                                f"**{source['filename']} — Page {source['page']}**"
                            )
                            st.write(source["text"])
                            st.caption(f"Chunk index: {source['chunk_index']}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"]
        })
