# Converting data into vectors
# Using Ollama to generate embeddings
# may take some time depending on the size of the dataframe

import ollama, json
import pandas as pd


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


def vectorize_dataframe(df):

    # df = pd.DataFrame(df, index=None)  # Ensure df is a DataFrame

    # Preprocess the DataFrame: strip whitespace and handle missing values
    df.map(lambda x: x.strip() if isinstance(x, str) else x).fillna('null')

    # Convert each row of the DataFrame to a JSON string
    df['json_data'] = df.apply(lambda row: row.to_json(), axis=1)
    # df['json_data'] = df.apply(lambda row: json.dumps(row.to_dict(), ensure_ascii=False), axis=1)

    df['embedding'] = None  # Initialize the embedding column

    # Generate embeddings for each row in the DataFrame
    for i, row in df.iterrows():
        # Convert the json string into a vector
        df.at[i, 'embedding'] = generate_embeddings(row['json_data'])

    return df