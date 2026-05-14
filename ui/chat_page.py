import streamlit as st

from services.vector_db_service import (
    search_vector_db,
    get_database_count
)


def build_basic_rag_response(user_question):
    """
    Temporary placeholder for the future LLM agent.

    Right now, this only retrieves relevant chunks from the vector DB.
    Later, this function can send the retrieved chunks and question to an LLM.
    """
    if get_database_count() == 0:
        return {
            "answer": "No documents have been uploaded yet. Please upload a PDF first.",
            "sources": []
        }

    results = search_vector_db(user_question, n_results=4)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "sources": []
        }

    answer = (
        "I found relevant information in the vector database. "
        "The LLM answer generation step has not been connected yet, "
        "but these are the retrieved chunks that would be sent to the LLM."
    )

    sources = []

    for document, metadata in zip(documents, metadatas):
        sources.append({
            "text": document,
            "filename": metadata["filename"],
            "page": metadata["page"],
            "chunk_index": metadata["chunk_index"]
        })

    return {
        "answer": answer,
        "sources": sources
    }


def render_chat_page():
    st.header("Chat with Your Study Agent")

    st.write(
        """
        This is where the user will eventually interact with the LLM.
        For now, the chat retrieves relevant chunks from the vector database
        so you can test whether the RAG pipeline is working.
        """
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

            if "sources" in message:
                with st.expander("Retrieved Sources"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**{source['filename']} — Page {source['page']}**"
                        )
                        st.write(source["text"])
                        st.caption(f"Chunk index: {source['chunk_index']}")

    user_question = st.chat_input("Ask something about your uploaded PDF...")

    if user_question:
        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.write(user_question)

        response = build_basic_rag_response(user_question)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"]
        })

        with st.chat_message("assistant"):
            st.write(response["answer"])

            if response["sources"]:
                with st.expander("Retrieved Sources"):
                    for source in response["sources"]:
                        st.markdown(
                            f"**{source['filename']} — Page {source['page']}**"
                        )
                        st.write(source["text"])
                        st.caption(f"Chunk index: {source['chunk_index']}")
