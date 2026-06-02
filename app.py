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

# Initialize active page
if "active_page" not in st.session_state:
    st.session_state.active_page = "Upload"

# Track the last selected documents page
if "last_documents_page" not in st.session_state:
    st.session_state.last_documents_page = "Upload"

documents_page = st.sidebar.radio(
    "Document Tools",
    [
        "Upload",
        "Database Status",
        "Test Search"
    ],
    index=["Upload", "Database Status", "Test Search"].index(st.session_state.last_documents_page),
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

st.sidebar.markdown("## Chat")

chat_selected = st.sidebar.button("Open Chat")


# -----------------------------
# Page Routing
# -----------------------------

# Update navigation based on user action
if chat_selected:
    st.session_state.active_page = "Chat"
elif documents_page != st.session_state.last_documents_page:
    # User selected a different documents page
    st.session_state.active_page = documents_page
    st.session_state.last_documents_page = documents_page
elif st.session_state.active_page not in ["Chat", "Upload", "Database Status", "Test Search"]:
    # Fallback to Upload if active_page is invalid
    st.session_state.active_page = "Upload"
# Otherwise, keep the current active_page (preserves Chat state during interactions)


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
