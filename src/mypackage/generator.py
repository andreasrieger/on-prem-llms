import ollama


# Generate answer based on prompt
def generate_answer(p, m='mistral'):
    return ollama.generate(
        model=m,
        prompt=p
    )
