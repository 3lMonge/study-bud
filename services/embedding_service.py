import streamlit as st
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "google/embeddinggemma-300m"


@st.cache_resource
def load_embedding_model():
    """
    Loads the EmbeddingGemma model once and caches it.

    Note:
        The first time this runs, it may download the model from Hugging Face.
        You may need to accept the Gemma license on Hugging Face first.
    """
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_text(text):
    """
    Converts text into an embedding vector.
    """
    model = load_embedding_model()
    return model.encode(text).tolist()


def get_embedding_model_name():
    """
    Returns the active embedding model name.
    """
    return EMBEDDING_MODEL_NAME
