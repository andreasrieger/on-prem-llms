import ollama

def generate(search_result,search_term,m,p):
    models = ['mistral','stablelm2','avr/sfr-embedding-mistral']
    prompts = [
        f"Welches Produkt aus {search_result[0].payload['product_name']} ist für {search_term} geeignet?",
        #f"perform search for {search_term} in {df_qrs} using the information schema in {df_knowledge}. then print list of matching product names with its product description.",
        #f"perform search for {search_term} using the information schema in {df_knowledge}. then print list of product names in {search_result[0].payload['product_name']} with its product description in {search_result[0].payload['product_description']} for all matching products."
    ]

    model = models[m]
    prompt = prompts[p]

    return ollama.generate(
        model=model,
        prompt=prompt
    )