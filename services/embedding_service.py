import streamlit as st
from sentence_transformers import SentenceTransformer


@st.cache_resource
def load_embedding_model():
    """
    Loads the embedding model once and caches it.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text):
    """
    Converts text into an embedding vector.
    """
    model = load_embedding_model()
    return model.encode(text).tolist()
