import ollama

# Function to generate embeddings
def generate_embeddings(o, m):
    return ollama.embeddings(m, o)["embedding"]