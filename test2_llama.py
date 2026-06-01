from llama_cpp import Llama

MODEL_PATH = "models/llama-3.2-3b-q4/llama-3.2-3b-instruct-q4_k_m.gguf"
print("Loading model...")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=1024,
    n_threads=4,
    n_gpu_layers=0,
    verbose=True
)

print("Model loaded.")
print("Generating response...")

response = llm(
    "Q: What is a RAG system? Answer in one short paragraph.\nA:",
    max_tokens=80,
    temperature=0.2,
    stop=["Q:"]
)

print("Response:")
print(response["choices"][0]["text"])
