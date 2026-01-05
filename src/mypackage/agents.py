# Generate SQL query based on user prompt
def agent_sql_query(q, k, m):
    # Create the agent information prompt
    agent_info = f"You are an AI language model assistant. Your task is to find matching products to the {q} using only results from a product database with this schema: {k}. All data are stored within one table. Create an SQL query that returns the product name aliases and descriptions of the matching products."
    res = generate_answer(agent_info, m)
    return res['response']


# Perform vector search based on user prompt
def agent_vector_search(q, k, m):

    print(f"model: {m}")

    # agent_info = f"You are an AI language model assistant. Your task is to find matching products to the {search_query} using only results from a product database that is described by {knowledge}. Create an embedding vector for the search term and use it to search the vector database for the most relevant products."
    # agent_info = f"Based on the following search result: {search_result[0].payload}, provide a concise answer about the product."
    agent_info = (
        f"You are an AI language model assistant. " +
        f"Your task is to find the top 3 most relevant matching products in a product database that is described by {k}. " +
        f"The search is performed using vector search with cosine similarity. The search term is {q}. " +
        f"Create a prompt for the vector search."
    )

    # print(f"agent_info: {agent_info}")

    res = generate_answer(agent_info, m)
    return res['response']
