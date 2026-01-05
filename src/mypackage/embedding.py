
# Converting data into vectors
# Using Ollama to generate embeddings
# may take some time depending on the size of the dataframe

import ollama, json, sys
import pandas as pd


# Function to generate embeddings
def get_embedding(query, model="mxbai-embed-large"): # byte size of vector is 8248
    return ollama.embeddings(model, query)["embedding"]


# Optional: Convert the embeddings string to a list of floats if necessary
def convert_str_to_list(obj):
    for i, row in obj.iterrows():
        embedding_list = row['embedding'].split(',')
        obj.at[i, 'embedding'] = [float(x) for x in embedding_list]
    return obj


#@andreasrieger: refactor to do only one thing
def vectorize_dataframe_columns(df):

    # df = pd.DataFrame(df, index=None)  # Ensure df is a DataFrame

    # Preprocess the DataFrame: strip whitespace and handle missing values
    df.map(lambda x: x.strip() if isinstance(x, str) else x).fillna('null')

    # Convert each row of the DataFrame to a JSON string
    df['json_data'] = df.apply(lambda row: row.to_json(), axis=1)
    # df['json_data'] = df.apply(lambda row: json.dumps(row.to_dict(), ensure_ascii=False), axis=1)

    df['embedding'] = None  # Initialize the embedding column

    # Generate embeddings for each row in the DataFrame
    for i, row in df.iterrows():
        # byte_sizes.append(sys.getsizeof(row['json_data']))
        # Convert the json string into a vector
        vec = get_embedding(row['json_data'])
        df.at[i, 'embedding'] = vec

    return df