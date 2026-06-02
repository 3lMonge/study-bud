import streamlit as st
import os

from services.vector_db_service import get_database_count
from services.agent_service import chat_with_agent


def render_chat_page():
    st.header("📚 StudyBud - Your AI Study Tutor")

    # Check if documents are uploaded
    if get_database_count() == 0:
        st.warning("⚠️ No documents uploaded yet. Please upload a PDF first from the Upload page.")
        st.info(
            """
            **How StudyBud works:**
            1. Upload your study materials (PDFs)
            2. StudyBud will help you:
               - Suggest chunks of material to study
               - Generate questions at different difficulty levels
               - Evaluate your answers and provide feedback
               - Summarize topics
            """
        )
        return

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error(
            """
            ⚠️ **ANTHROPIC_API_KEY not found**
            
            Please set your Anthropic API key as an environment variable:
            ```bash
            export ANTHROPIC_API_KEY=sk-ant-...
            ```
            """
        )
        return

    st.write(
        """
        Welcome! I'm StudyBud, your AI study tutor. I can help you master your study materials through:
        - 📖 Suggesting focused study chunks
        - ❓ Generating quiz questions (easy/medium/hard)
        - ✅ Evaluating your answers with detailed feedback
        - 📝 Summarizing topics
        """
    )

    # Difficulty selector in sidebar or above chat
    st.sidebar.markdown("---")
    st.sidebar.subheader("Study Settings")
    
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "medium"
    
    difficulty = st.sidebar.radio(
        "Default Question Difficulty",
        ["easy", "medium", "hard"],
        index=["easy", "medium", "hard"].index(st.session_state.difficulty),
        help="Easy: recall/definition | Medium: comprehension | Hard: analysis/synthesis"
    )
    st.session_state.difficulty = difficulty

    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Actions")
    
    if st.sidebar.button("📖 Suggest Study Chunk"):
        quick_input = "Suggest a focused chunk of material for me to study right now."
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({
            "role": "user",
            "content": quick_input
        })
        st.rerun()
    
    if st.sidebar.button(f"❓ Quiz Me ({difficulty})"):
        quick_input = f"Quiz me with a {difficulty} difficulty question."
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({
            "role": "user",
            "content": quick_input
        })
        st.rerun()
    
    if st.sidebar.button("📋 List Topics"):
        quick_input = "List all topics covered in the loaded documents."
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({
            "role": "user",
            "content": quick_input
        })
        st.rerun()
    
    if st.sidebar.button("📝 Summarize Materials"):
        quick_input = "Give me a concise summary of all the study materials."
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({
            "role": "user",
            "content": quick_input
        })
        st.rerun()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_question = st.chat_input("Ask me anything about your study materials...")

    if user_question:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get chat history without the current message
                    history = st.session_state.messages[:-1]
                    
                    # Get response from agent
                    response = chat_with_agent(
                        user_input=user_question,
                        chat_history=history,
                        api_key=api_key
                    )
                    
                    st.markdown(response)
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
