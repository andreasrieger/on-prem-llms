# Converting data into vectors
# Using Ollama to generate embeddings
# may take some time depending on the size of the dataframe

import ollama
from modules import qdrant


# Function to generate embeddings
def generate_embeddings(obj):
    model = "mxbai-embed-large"
    return ollama.embeddings(model, obj)["embedding"]


# Optional: Convert the embeddings string to a list of floats if necessary
def convert_str_to_list(obj):
    for i, row in obj.iterrows():
        embedding_list = row['embedding'].split(',')
        obj.at[i, 'embedding'] = [float(x) for x in embedding_list]
    return obj


def something(obj, collection_name):
    # res = obj[0].assign(embedding=None)

    # Generate embeddings for each row in the DataFrame
    for i, row in res.iterrows(): # using iterrows() in a DataFrame?
        # Convert the json string into a vector
        res.at[i, 'embedding'] = generate_embeddings(row['json'])

    # Store the vectors in Qdrant
    return qdrant.store_vectors_in_qdrant(res, collection_name=collection_name)
