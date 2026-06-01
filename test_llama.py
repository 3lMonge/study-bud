from llama_cpp import Llama

llm = Llama(
    model_path="models/llama-3.2-3b-q4/llama-3.2-3b-instruct-q4_k_m.gguf",
    n_ctx=2048,
    n_gpu_layers=0,
    verbose=False
)

response = llm(
    "Explain what a RAG system is in simple terms.",
    max_tokens=150,
    temperature=0.2
)

print(response["choices"][0]["text"])
