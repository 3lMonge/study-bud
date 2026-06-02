"""
Study Agent — LangChain + Anthropic
====================================
Agentic tutor that reads uploaded documents and helps students study
through adaptive quizzing, chunked study suggestions, and feedback.

Your partner's document-upload module just needs to drop files into
the ./documents/ folder (PDF, TXT, MD, DOCX) before starting a session.
"""

import os
from pathlib import Path
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from rich import print as rprint

console = Console()

# ---------------------------------------------------------------------------
# Document loading (black-box interface for your partner)
# ---------------------------------------------------------------------------

DOCS_DIR = Path(__file__).parent / "documents"
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".md", ".docx"}

def load_documents(docs_dir: Path = DOCS_DIR) -> list[Document]:
    """
    Load all supported documents from docs_dir.
    Your partner's upload module should place files here.
    Returns a flat list of LangChain Document objects with metadata.
    """
    docs_dir.mkdir(exist_ok=True)
    all_docs: list[Document] = []
    files_found = list(docs_dir.iterdir())

    if not files_found:
        console.print(
            "[yellow]No documents found in ./documents/ — loading demo content.[/yellow]"
        )
        return _load_demo_documents()

    for path in files_found:
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            loader_map = {
                ".txt":  TextLoader,
                ".md":   UnstructuredMarkdownLoader,
                ".pdf":  PyPDFLoader,
                ".docx": Docx2txtLoader,
            }
            loader_cls = loader_map[path.suffix.lower()]
            loader = loader_cls(str(path))
            docs = loader.load()
            for d in docs:
                d.metadata["source_file"] = path.name
            all_docs.extend(docs)
            console.print(f"  [green]✓[/green] Loaded [bold]{path.name}[/bold]")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed to load {path.name}: {e}")

    return all_docs


def _load_demo_documents() -> list[Document]:
    """Fallback demo content when no files are present."""
    demo = [
        Document(
            page_content=(
                "Photosynthesis is the process by which plants, algae, and some bacteria "
                "convert light energy into chemical energy stored as glucose. "
                "Overall equation: 6CO2 + 6H2O + light → C6H12O6 + 6O2. "
                "It has two stages: light-dependent reactions (thylakoid membranes) and "
                "the Calvin cycle (stroma). Light reactions produce ATP and NADPH and "
                "release O2. The Calvin cycle fixes CO2 into glucose via RuBisCO. "
                "Chlorophyll a/b absorb red and blue light. Rate is affected by light "
                "intensity, CO2 concentration, temperature, and water availability."
            ),
            metadata={"source_file": "demo_ch1_photosynthesis.txt"},
        ),
        Document(
            page_content=(
                "Cell division allows organisms to grow, repair tissue, and reproduce. "
                "Mitosis produces two genetically identical diploid daughter cells "
                "(prophase → metaphase → anaphase → telophase → cytokinesis). "
                "Meiosis produces four haploid gametes through two rounds of division. "
                "Crossing over in prophase I generates genetic variation. "
                "The cell cycle: interphase (G1, S, G2) + mitotic phase. "
                "G1, G2, and spindle assembly checkpoints ensure accuracy."
            ),
            metadata={"source_file": "demo_ch2_cell_division.txt"},
        ),
        Document(
            page_content=(
                "Genetics studies heredity and variation. Mendel's laws: "
                "Law of Segregation (alleles separate during gamete formation) and "
                "Law of Independent Assortment (genes on different chromosomes assort "
                "independently). Dominant alleles mask recessive ones. "
                "DNA is a double helix of nucleotides (A, T, G, C). "
                "Mutations can be point mutations, insertions, or deletions. "
                "Punnett squares predict offspring genotype ratios. "
                "Incomplete dominance and codominance are non-Mendelian exceptions. "
                "Sex-linked traits are carried on X or Y chromosomes."
            ),
            metadata={"source_file": "demo_ch3_genetics.txt"},
        ),
    ]
    return demo


def build_document_context(docs: list[Document]) -> str:
    """Concatenate all document content into a single context string for the agent."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    sections = []
    for chunk in chunks:
        source = chunk.metadata.get("source_file", "unknown")
        sections.append(f"[Source: {source}]\n{chunk.page_content}")
    return "\n\n---\n\n".join(sections)


# ---------------------------------------------------------------------------
# LangChain Tools
# ---------------------------------------------------------------------------

# We attach the document context to tools via a module-level variable so tools
# (which must be plain functions) can access it without extra arguments.
_DOC_CONTEXT: str = ""
_DIFFICULTY: str = "medium"


@tool
def suggest_study_chunk(topic: Optional[str] = None) -> str:
    """
    Suggest a focused chunk of material for the student to study right now.
    Breaks content into 2-4 key concepts and cites the source document.
    Optionally accepts a topic to focus on.
    """
    focus = f" Focus on the topic: {topic}." if topic else ""
    return (
        f"Using the study materials below, recommend a focused study chunk of 2-4 key "
        f"concepts the student should read right now.{focus} Cite which source file each "
        f"concept comes from. Format as a short bullet-point study guide.\n\n"
        f"MATERIALS:\n{_DOC_CONTEXT}"
    )


@tool
def generate_question(difficulty: str = "medium", topic: Optional[str] = None) -> str:
    """
    Generate a single study question at the given difficulty level.
    difficulty: 'easy' | 'medium' | 'hard'
    Easy = recall/definition. Medium = comprehension/application. Hard = analysis/synthesis.
    Optionally focuses on a specific topic.
    """
    focus = f" Focus on topic: {topic}." if topic else ""
    return (
        f"Generate exactly ONE {difficulty}-difficulty question to test the student's "
        f"understanding of the study materials.{focus} "
        f"Label it with [{difficulty.capitalize()}] at the start. "
        f"Ask the question only — do not provide the answer yet.\n\n"
        f"MATERIALS:\n{_DOC_CONTEXT}"
    )


@tool
def evaluate_answer(question: str, student_answer: str, difficulty: str = "medium") -> str:
    """
    Evaluate the student's answer to a question. Provide constructive feedback,
    correct any misconceptions, and award partial credit where deserved.
    """
    return (
        f"The student was asked this question:\n{question}\n\n"
        f"Their answer was:\n{student_answer}\n\n"
        f"Evaluate their answer based on the study materials. Be encouraging and "
        f"specific about what they got right. Gently correct any misconceptions. "
        f"If partially correct, explain what was missing. "
        f"End with a brief explanation of the full correct answer.\n\n"
        f"MATERIALS:\n{_DOC_CONTEXT}"
    )


@tool
def summarize_topic(topic: Optional[str] = None) -> str:
    """
    Produce a concise summary of study materials, optionally focused on a topic.
    """
    focus = f" Focus on: {topic}." if topic else " Cover all major topics."
    return (
        f"Write a concise summary of the key concepts in the study materials.{focus} "
        f"Use bullet points grouped by source document. Keep it scannable.\n\n"
        f"MATERIALS:\n{_DOC_CONTEXT}"
    )


@tool
def list_topics() -> str:
    """List all major topics and concepts covered across the loaded study materials."""
    return (
        f"List all the major topics and sub-topics covered in the study materials. "
        f"Group them by source document. This helps the student know what they can be quizzed on.\n\n"
        f"MATERIALS:\n{_DOC_CONTEXT}"
    )


TOOLS = [suggest_study_chunk, generate_question, evaluate_answer, summarize_topic, list_topics]


# ---------------------------------------------------------------------------
# Agent setup
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert, encouraging study tutor called Study Agent. \
Your job is to help students learn through active recall and spaced practice.

You have access to the following tools:
- suggest_study_chunk: recommend a focused chunk of material to study
- generate_question: create a quiz question at easy/medium/hard difficulty
- evaluate_answer: assess the student's answer and give feedback
- summarize_topic: produce a summary of the material
- list_topics: show what topics are available in the loaded documents

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
"""


def build_agent(api_key: str) -> AgentExecutor:
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=False, max_iterations=5)


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

DIFFICULTY_COLORS = {"easy": "green", "medium": "yellow", "hard": "red"}
QUICK_COMMANDS = {
    "/suggest":  "Suggest what I should study right now.",
    "/quiz":     "Quiz me with a question at my current difficulty level.",
    "/summary":  "Summarize all the study materials.",
    "/topics":   "List all topics covered in the documents.",
    "/easy":     None,  # handled separately
    "/medium":   None,
    "/hard":     None,
    "/help":     None,
    "/quit":     None,
}


def print_welcome(doc_names: list[str], difficulty: str):
    console.print()
    console.print(Panel.fit(
        "[bold]Study Agent[/bold]  —  LangChain + Anthropic\n"
        "[dim]Adaptive tutor powered by your uploaded documents[/dim]",
        border_style="blue",
    ))
    console.print()
    console.print("[bold]Loaded documents:[/bold]")
    for name in doc_names:
        console.print(f"  [green]•[/green] {name}")
    console.print()
    console.print(f"[bold]Difficulty:[/bold] [{DIFFICULTY_COLORS[difficulty]}]{difficulty}[/{DIFFICULTY_COLORS[difficulty]}]")
    console.print()
    console.print("[dim]Quick commands:[/dim]")
    for cmd, desc in QUICK_COMMANDS.items():
        if desc:
            console.print(f"  [cyan]{cmd}[/cyan]  {desc}")
    console.print(f"  [cyan]/easy /medium /hard[/cyan]  Change difficulty")
    console.print(f"  [cyan]/quit[/cyan]  Exit")
    console.print()


def run_cli():
    global _DOC_CONTEXT, _DIFFICULTY

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set.")
        return

    console.print("[dim]Loading documents...[/dim]")
    docs = load_documents()
    _DOC_CONTEXT = build_document_context(docs)
    doc_names = sorted({d.metadata.get("source_file", "unknown") for d in docs})

    agent_executor = build_agent(api_key)
    chat_history: list = []
    _DIFFICULTY = "medium"
    last_question: Optional[str] = None

    print_welcome(doc_names, _DIFFICULTY)

    # Kick off with an intro
    with console.status("[dim]Study Agent is thinking...[/dim]", spinner="dots"):
        response = agent_executor.invoke({
            "input": "Hello! Briefly introduce yourself, list the topics available, and ask if the student is ready to begin.",
            "chat_history": chat_history,
        })
    reply = response["output"]
    console.print(Panel(Markdown(reply), title="[blue]Study Agent[/blue]", border_style="blue", padding=(1, 2)))
    chat_history.extend([HumanMessage(content="Hello!"), AIMessage(content=reply)])

    # Main loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye! Keep studying![/dim]")
            break

        if not user_input:
            continue

        # Handle slash commands
        lower = user_input.lower()
        if lower == "/quit":
            console.print("[dim]Goodbye! Keep studying![/dim]")
            break
        elif lower in ("/easy", "/medium", "/hard"):
            _DIFFICULTY = lower[1:]
            color = DIFFICULTY_COLORS[_DIFFICULTY]
            console.print(f"[{color}]Difficulty set to {_DIFFICULTY}.[/{color}]")
            continue
        elif lower == "/help":
            for cmd, desc in QUICK_COMMANDS.items():
                if desc:
                    console.print(f"  [cyan]{cmd}[/cyan]  {desc}")
            continue
        elif lower == "/quiz":
            user_input = f"Quiz me with a [{_DIFFICULTY}] difficulty question."
        elif lower == "/suggest":
            user_input = "Suggest a focused chunk of material for me to study right now."
        elif lower == "/summary":
            user_input = "Give me a concise summary of all the study materials."
        elif lower == "/topics":
            user_input = "List all topics covered in the loaded documents."

        # If the last agent message contained a question, treat this input as an answer
        if last_question and not lower.startswith("/"):
            user_input = (
                f"My answer to your question '{last_question}' is: {user_input}\n"
                f"Please evaluate my answer."
            )

        with console.status("[dim]Study Agent is thinking...[/dim]", spinner="dots"):
            try:
                response = agent_executor.invoke({
                    "input": user_input,
                    "chat_history": chat_history,
                })
                reply = response["output"]
            except Exception as e:
                console.print(f"[red]Agent error:[/red] {e}")
                continue

        console.print()
        console.print(Panel(
            Markdown(reply),
            title="[blue]Study Agent[/blue]",
            border_style="blue",
            padding=(1, 2),
        ))

        chat_history.extend([HumanMessage(content=user_input), AIMessage(content=reply)])

        # Detect if agent just asked a question (so next input is treated as answer)
        reply_lower = reply.lower()
        if "?" in reply and any(k in reply_lower for k in ["[easy]", "[medium]", "[hard]", "question:"]):
            last_question = reply.strip()
        else:
            last_question = None

        # Keep history bounded to last 20 messages
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_cli()
