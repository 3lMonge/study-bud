import streamlit as st
from llama_cpp import Llama


LLM_MODEL_NAME = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
LLM_MODEL_PATH = "models/llama-3.2-3b-q4/llama-3.2-3b-instruct-q4_k_m.gguf"


@st.cache_resource
def load_llm():
    """
    Loads the local GGUF Llama model once and caches it.

    n_ctx controls the context window.
    n_gpu_layers=-1 tries to use GPU acceleration if available.
    If this causes problems, change n_gpu_layers to 0.
    """
    return Llama(
        model_path=LLM_MODEL_PATH,
        n_ctx=4096,
        n_gpu_layers=-1,
        verbose=False
    )


def get_llm_model_name():
    """
    Returns the active local LLM model name.
    """
    return LLM_MODEL_NAME


def build_rag_prompt(question, sources):
    """
    Builds the prompt sent to the local Llama model.

    The model should answer only using the retrieved document chunks.
    """

    context_blocks = []

    for i, source in enumerate(sources, start=1):
        block = f"""
Source {i}
Filename: {source["filename"]}
Page: {source["page"]}
Text:
{source["text"]}
"""
        context_blocks.append(block)

    context = "\n\n".join(context_blocks)

    prompt = f"""
You are a helpful study assistant.

Answer the user's question using only the provided document sources.

Rules:
- Do not invent information.
- If the answer is not in the sources, say that the uploaded document does not provide enough information.
- Explain the answer clearly for a student.
- Include page references when possible.
- Use this citation format: (filename, p. page number)

Document Sources:
{context}

User Question:
{question}

Answer:
"""

    return prompt


def generate_answer(question, sources):
    """
    Generates an answer using the local Llama model.
    """

    if not sources:
        return "I could not find relevant sources in the selected document."

    llm = load_llm()

    prompt = build_rag_prompt(question, sources)

    response = llm(
        prompt,
        max_tokens=700,
        temperature=0.2,
        top_p=0.9,
        stop=["User Question:", "Document Sources:"]
    )

    answer = response["choices"][0]["text"].strip()

    return answer
