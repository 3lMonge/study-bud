import streamlit as st

from ui.documents_page import (
    render_upload_page,
    render_database_status_page,
    render_test_search_page
)

from ui.chat_page import render_chat_page

from services.vector_db_service import get_database_info


st.set_page_config(
    page_title="Study Agent",
    #page_icon="📚",
    layout="wide"
)


# -----------------------------
# Custom CSS
# -----------------------------

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        position: relative;
    }

    .sidebar-status {
        position: fixed;
        bottom: 20px;
        width: 260px;
        padding: 12px;
        border-radius: 10px;
        background-color: rgba(240, 242, 246, 0.9);
        font-size: 0.85rem;
    }

    .sidebar-status-title {
        font-weight: 700;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Sidebar Navigation
# -----------------------------

st.sidebar.title("Study Agent")

st.sidebar.markdown("## Documents")

documents_page = st.sidebar.radio(
    "Document Tools",
    [
        "Upload",
        "Database Status",
        "Test Search"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

st.sidebar.markdown("## Chat")

chat_selected = st.sidebar.button("Open Chat")


# -----------------------------
# Page Routing
# -----------------------------

if "active_page" not in st.session_state:
    st.session_state.active_page = "Upload"

if chat_selected:
    st.session_state.active_page = "Chat"
else:
    st.session_state.active_page = documents_page


st.title("StudyBud")

if st.session_state.active_page == "Upload":
    render_upload_page()

elif st.session_state.active_page == "Database Status":
    render_database_status_page()

elif st.session_state.active_page == "Test Search":
    render_test_search_page()

elif st.session_state.active_page == "Chat":
    render_chat_page()


# -----------------------------
# Sidebar Bottom Status
# -----------------------------

db_info = get_database_info()

st.sidebar.markdown(
    f"""
    <div class="sidebar-status">
        <div class="sidebar-status-title">Vector DB Status</div>
        <div><strong>Stored Chunks:</strong> {db_info["stored_chunks"]}</div>
        <div><strong>Database:</strong> {db_info["db_path"]}</div>
        <div><strong>Collection:</strong> {db_info["collection_name"]}</div>
    </div>
    """,
    unsafe_allow_html=True
)
