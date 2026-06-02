# StudyBud - AI Study Tutor

An agentic study tutor built with **LangChain**, **Anthropic Claude**, and **Streamlit**.  
StudyBud helps students master their study materials through adaptive quizzing, chunked study suggestions, and detailed answer feedback.

---

## Features

🎯 **Adaptive Quizzing**: Generate questions at three difficulty levels
- **Easy**: Recall and definition questions
- **Medium**: Comprehension and application questions  
- **Hard**: Analysis and synthesis questions

📖 **Smart Study Chunks**: Get AI-suggested reasonable chunks of material to study before quizzing

✅ **Answer Evaluation**: Receive detailed, constructive feedback on your answers

📝 **Topic Summaries**: Get concise summaries of your study materials

🔍 **Semantic Search**: Ask questions and get answers grounded in your documents

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or add it to your environment permanently.

### 3. Run the Streamlit app

```bash
streamlit run app.py
```

---

## Usage

### Upload Documents

1. Navigate to the **Upload** page in the sidebar
2. Upload your PDF study materials
3. Click "Extract and Store in Vector DB"
4. Your documents are now processed and ready for studying

### Chat with StudyBud

1. Click **Open Chat** in the sidebar
2. Use the quick actions:
   - 📖 **Suggest Study Chunk**: Get a focused section to study
   - ❓ **Quiz Me**: Get a question at your selected difficulty
   - 📋 **List Topics**: See all available topics
   - 📝 **Summarize**: Get a summary of materials

3. Or type your own questions:
   - "What topics can you quiz me on?"
   - "Give me a hard question about photosynthesis"
   - "Suggest what I should study next"
   - "Summarize the main concepts"

### Study Workflow

**Recommended approach:**
1. Start by asking for a **study chunk suggestion**
2. Review the suggested material
3. Request a **quiz question** on that topic
4. Answer the question
5. Get **detailed feedback** on your answer
6. Repeat with different topics or difficulty levels

---

## Project Structure

```
study-bud/
├── app.py                      # Main Streamlit app
├── agent.py                    # Standalone CLI agent (legacy)
├── requirements.txt            # Python dependencies
├── services/
│   ├── agent_service.py        # LangChain agent logic
│   ├── chunking_service.py     # Text chunking
│   ├── embedding_service.py    # Vector embeddings
│   ├── pdf_service.py          # PDF processing
│   └── vector_db_service.py    # ChromaDB integration
├── ui/
│   ├── chat_page.py            # Chat interface
│   └── documents_page.py       # Document management UI
└── chroma_db/                  # Vector database (auto-created)
```

---

## Advanced Usage

### CLI Mode (Legacy)

You can also run the standalone CLI agent:

```bash
python agent.py
```

Place documents in `./documents/` folder before running.

### Difficulty Levels

- **Easy**: Tests basic recall (e.g., "What is photosynthesis?")
- **Medium**: Tests understanding (e.g., "Why does temperature affect photosynthesis?")
- **Hard**: Tests analysis (e.g., "Design an experiment to measure photosynthesis rate")

---

## Technologies

- **LangChain**: Agent orchestration and tool calling
- **Anthropic Claude Sonnet 4**: Large language model
- **Streamlit**: Web interface
- **ChromaDB**: Vector database for semantic search
- **Sentence Transformers**: Text embeddings

If no documents are found, the agent falls back to built-in demo biology content so you can test immediately.

### 4. Run the agent

```bash
python agent.py
```

---

## Usage

Once running, type naturally or use quick commands:

| Command | Action |
|---------|--------|
| `/suggest` | Agent recommends a focused chunk to study |
| `/quiz` | Agent asks one question at current difficulty |
| `/summary` | Concise summary of all loaded materials |
| `/topics` | Lists all topics available for quizzing |
| `/easy` | Set difficulty to easy (recall/definition) |
| `/medium` | Set difficulty to medium (comprehension) |
| `/hard` | Set difficulty to hard (analysis/synthesis) |
| `/quit` | Exit |

You can also just type naturally — ask questions, answer quizzes, or request explanations.

---

## Architecture

```
agent.py
├── load_documents()        # Loads files from ./documents/ via LangChain loaders
├── build_document_context()# Chunks + concatenates docs for the agent's context
│
├── Tools (LangChain @tool)
│   ├── suggest_study_chunk   # Recommends what to study next
│   ├── generate_question     # Creates a question at the given difficulty
│   ├── evaluate_answer       # Grades the student's answer with feedback
│   ├── summarize_topic       # Produces a topic summary
│   └── list_topics           # Lists all covered topics
│
├── build_agent()           # create_tool_calling_agent + AgentExecutor
└── run_cli()               # Rich-powered interactive CLI loop
```

The agent uses `create_tool_calling_agent` with a `ChatPromptTemplate` that includes a persistent `chat_history` placeholder, giving it memory across the session. History is capped at 20 messages to stay within context limits.

---

## Difficulty levels

| Level | Question style |
|-------|---------------|
| Easy | Recall and definition ("What is...?", "Name the stages of...") |
| Medium | Comprehension and application ("Why does...?", "Compare X and Y") |
| Hard | Analysis and synthesis ("Explain the mechanism...", "Design an experiment...") |

---

## Extending

- **Swap the model**: change `model="claude-sonnet-4-20250514"` in `build_agent()` to any Anthropic model string.
- **Add vector search**: replace `build_document_context()` with a FAISS or Chroma retriever for larger document sets.
- **Plug in a web UI**: `build_agent()` returns a plain `AgentExecutor` — wrap `run_cli()` with FastAPI + WebSocket for a browser frontend.
