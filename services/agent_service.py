"""
Study Agent Service — LangChain + Anthropic
============================================
Agentic tutor that helps students study through adaptive quizzing,
chunked study suggestions, and feedback using vector DB content.
"""

import os
from typing import Optional, List, Dict, Any

from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from services.vector_db_service import search_vector_db, get_database_count


# ---------------------------------------------------------------------------
# Document Context Management
# ---------------------------------------------------------------------------

def get_document_context(query: Optional[str] = None, n_results: int = 10) -> str:
    """
    Retrieve relevant document chunks from the vector DB.
    If query is provided, searches for relevant content.
    Otherwise, returns a sample of stored content.
    """
    if get_database_count() == 0:
        return "No documents have been uploaded yet."
    
    if query:
        results = search_vector_db(query, n_results=n_results)
    else:
        # Get some random content to provide general context
        results = search_vector_db("overview summary introduction", n_results=n_results)
    
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    
    if not documents:
        return "No relevant content found in the uploaded documents."
    
    sections = []
    for doc, meta in zip(documents, metadatas):
        source = f"{meta.get('filename', 'unknown')} (page {meta.get('page', '?')})"
        sections.append(f"[Source: {source}]\n{doc}")
    
    return "\n\n---\n\n".join(sections)


def get_topics_context() -> str:
    """
    Get a broad sample of content from various topics in the vector DB.
    """
    if get_database_count() == 0:
        return "No documents uploaded yet."
    
    # Search for diverse content
    queries = ["introduction overview", "key concepts", "important definitions", "main topics"]
    all_docs = []
    
    for query in queries:
        results = search_vector_db(query, n_results=3)
        docs = results.get("documents", [[]])[0]
        all_docs.extend(docs)
    
    # Deduplicate and limit
    unique_docs = list(set(all_docs))[:15]
    return "\n\n".join(unique_docs)


# ---------------------------------------------------------------------------
# LangChain Tools
# ---------------------------------------------------------------------------

@tool
def suggest_study_chunk(topic: Optional[str] = None) -> str:
    """
    Suggest a focused chunk of material for the student to study right now.
    Breaks content into 2-4 key concepts and cites the source document.
    Optionally accepts a topic to focus on.
    """
    if topic:
        context = get_document_context(query=topic, n_results=8)
        focus = f" Focus on the topic: {topic}."
    else:
        context = get_document_context(query="overview introduction key concepts", n_results=8)
        focus = ""
    
    return (
        f"Using the study materials below, recommend a focused study chunk of 2-4 key "
        f"concepts the student should read right now.{focus} Cite which source file and page "
        f"each concept comes from. Format as a short bullet-point study guide.\n\n"
        f"MATERIALS:\n{context}"
    )


@tool
def generate_question(difficulty: str = "medium", topic: Optional[str] = None) -> str:
    """
    Generate a single study question at the given difficulty level.
    difficulty: 'easy' | 'medium' | 'hard'
    Easy = recall/definition. Medium = comprehension/application. Hard = analysis/synthesis.
    Optionally focuses on a specific topic.
    """
    if topic:
        context = get_document_context(query=topic, n_results=6)
        focus = f" Focus on topic: {topic}."
    else:
        context = get_document_context(n_results=6)
        focus = ""
    
    return (
        f"Generate exactly ONE {difficulty}-difficulty question to test the student's "
        f"understanding of the study materials.{focus} "
        f"Label it with [{difficulty.capitalize()}] at the start. "
        f"Ask the question only — do not provide the answer yet.\n\n"
        f"Difficulty levels:\n"
        f"- Easy: recall/definition (What is...? Name the...)\n"
        f"- Medium: comprehension/application (Why does...? How would...? Compare...)\n"
        f"- Hard: analysis/synthesis (Explain the mechanism... Design an experiment...)\n\n"
        f"MATERIALS:\n{context}"
    )


@tool
def evaluate_answer(question: str, student_answer: str) -> str:
    """
    Evaluate the student's answer to a question. Provide constructive feedback,
    correct any misconceptions, and award partial credit where deserved.
    """
    # Search for relevant content based on the question
    context = get_document_context(query=question, n_results=5)
    
    return (
        f"The student was asked this question:\n{question}\n\n"
        f"Their answer was:\n{student_answer}\n\n"
        f"Evaluate their answer based on the study materials. Be encouraging and "
        f"specific about what they got right. Gently correct any misconceptions. "
        f"If partially correct, explain what was missing. "
        f"End with a brief explanation of the full correct answer.\n\n"
        f"MATERIALS:\n{context}"
    )


@tool
def summarize_topic(topic: Optional[str] = None) -> str:
    """
    Produce a concise summary of study materials, optionally focused on a topic.
    """
    if topic:
        context = get_document_context(query=topic, n_results=8)
        focus = f" Focus on: {topic}."
    else:
        context = get_topics_context()
        focus = " Cover all major topics."
    
    return (
        f"Write a concise summary of the key concepts in the study materials.{focus} "
        f"Use bullet points grouped by source document and page. Keep it scannable.\n\n"
        f"MATERIALS:\n{context}"
    )


@tool
def list_topics() -> str:
    """
    List all major topics and concepts covered across the loaded study materials.
    """
    context = get_topics_context()
    
    return (
        f"List all the major topics and sub-topics covered in the study materials. "
        f"Group them by source document. This helps the student know what they can be quizzed on.\n\n"
        f"MATERIALS:\n{context}"
    )


@tool
def search_materials(query: str) -> str:
    """
    Search the study materials for specific content related to a query.
    Returns the most relevant passages.
    """
    context = get_document_context(query=query, n_results=5)
    
    return (
        f"Search results for '{query}':\n\n{context}\n\n"
        f"Provide a clear answer to the student's query based on these materials."
    )


TOOLS = [
    suggest_study_chunk,
    generate_question,
    evaluate_answer,
    summarize_topic,
    list_topics,
    search_materials,
]


# ---------------------------------------------------------------------------
# Agent Setup
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert, encouraging study tutor called StudyBud. \
Your job is to help students learn through active recall and spaced practice.

You have access to the following tools:
- suggest_study_chunk: recommend a focused chunk of material to study
- generate_question: create a quiz question at easy/medium/hard difficulty
- evaluate_answer: assess the student's answer and give feedback
- summarize_topic: produce a summary of the material
- list_topics: show what topics are available in the loaded documents
- search_materials: search for specific content in the materials

Guidelines:
- Always use tools to ground your responses in the actual study materials.
- When quizzing, ask ONE question at a time and wait for the student's answer.
- Be warm, specific, and pedagogically sound.
- Difficulty levels:
    easy   → recall/definition ("What is...?", "Name the stages of...")
    medium → comprehension/application ("Why does...?", "Compare...")
    hard   → analysis/synthesis ("Explain the mechanism...", "Design an experiment...")
- After the student answers, use evaluate_answer to give structured feedback.
- Track what topics have been covered and vary your questions.
- If the student seems confused, suggest they re-read a specific section.
- When students first greet you, briefly introduce yourself and offer to help them study.
- You can suggest study strategies like: reviewing a chunk before quizzing, or working through topics systematically.
"""


def build_agent(api_key: str) -> AgentExecutor:
    """
    Build the LangChain agent executor with Anthropic Claude.
    """
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        max_tokens=2048,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=False,
        max_iterations=5,
        handle_parsing_errors=True,
    )


# ---------------------------------------------------------------------------
# Session Management
# ---------------------------------------------------------------------------

def get_agent(api_key: Optional[str] = None) -> AgentExecutor:
    """
    Get or create the agent executor.
    """
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    return build_agent(api_key)


def format_chat_history(messages: List[Dict[str, str]]) -> List:
    """
    Convert Streamlit message format to LangChain message format.
    """
    langchain_messages = []
    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    return langchain_messages


def chat_with_agent(
    user_input: str,
    chat_history: List[Dict[str, str]],
    api_key: Optional[str] = None
) -> str:
    """
    Send a message to the agent and get a response.
    
    Args:
        user_input: The user's message
        chat_history: List of previous messages in Streamlit format
        api_key: Optional Anthropic API key
    
    Returns:
        The agent's response
    """
    agent = get_agent(api_key)
    langchain_history = format_chat_history(chat_history)
    
    # Keep history bounded to last 20 messages
    if len(langchain_history) > 20:
        langchain_history = langchain_history[-20:]
    
    response = agent.invoke({
        "input": user_input,
        "chat_history": langchain_history,
    })
    
    output = response["output"]
    
    # Extract text from structured response if needed
    if isinstance(output, list):
        # Response is a list of content blocks
        text_parts = []
        for block in output:
            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
            elif isinstance(block, str):
                text_parts.append(block)
        return "\n".join(text_parts)
    elif isinstance(output, str):
        return output
    else:
        return str(output)
