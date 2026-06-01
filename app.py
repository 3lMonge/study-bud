import streamlit as st

from ui.home_page import render_home_page
from ui.upload_page import render_upload_page
from ui.select_page import render_select_page
from ui.chat_page import render_chat_page
from ui.test_page import render_test_page

from services.vector_db_service import get_database_info


st.set_page_config(
    page_title="Study Agent",
    #page_icon="📚",
    layout="wide"
)


# -----------------------------
# Session State
# -----------------------------

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

if "selected_documents" not in st.session_state:
    st.session_state.selected_documents = []


# -----------------------------
# Sidebar Navigation
# -----------------------------

st.sidebar.title("Study Agent")

if st.sidebar.button("Home", use_container_width=True):
    st.session_state.active_page = "Home"

if st.sidebar.button("Upload", use_container_width=True):
    st.session_state.active_page = "Upload"

if st.sidebar.button("Select", use_container_width=True):
    st.session_state.active_page = "Select"

if st.sidebar.button("Chat", use_container_width=True):
    st.session_state.active_page = "Chat"

if st.sidebar.button("Test", use_container_width=True):
    st.session_state.active_page = "Test"


# -----------------------------
# Main Page Routing
# -----------------------------

if st.session_state.active_page == "Home":
    render_home_page()

elif st.session_state.active_page == "Upload":
    render_upload_page()

elif st.session_state.active_page == "Select":
    render_select_page()

elif st.session_state.active_page == "Chat":
    render_chat_page()

elif st.session_state.active_page == "Test":
    render_test_page()


# -----------------------------
# Sidebar Status
# -----------------------------

st.sidebar.divider()

db_info = get_database_info()
selected_docs = st.session_state.get("selected_documents", [])

if selected_docs:
    selected_text = f"{len(selected_docs)} selected"
else:
    selected_text = "None"

st.sidebar.subheader("Vector DB Status")

st.sidebar.write(f"**Stored Chunks:** {db_info['stored_chunks']}")
st.sidebar.write(f"**Documents:** {db_info['document_count']}")
st.sidebar.write(f"**Selected:** {selected_text}")
st.sidebar.write(f"**Collection:** {db_info['collection_name']}")
