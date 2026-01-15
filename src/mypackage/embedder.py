# Converting data into vectors
# Using Ollama to generate embeddings
# may take some time depending on the size of the dataframe

import ollama

# Function to generate embeddings
def get_embedding(query, model="mxbai-embed-large"): # byte size of vector is 8248
    return ollama.embeddings(model, query)["embedding"]


# Optional: Convert the embeddings string to a list of floats if necessary
def convert_str_to_list(obj):
    for i, row in obj.iterrows():
        embedding_list = row['embedding'].split(',')
        obj.at[i, 'embedding'] = [float(x) for x in embedding_list]
    return obj
