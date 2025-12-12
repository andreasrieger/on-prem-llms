import json
import pandas as pd
import numpy as np
from modules import userinput
from modules import filehandler
from modules.embedding import generate_embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams


# Function to keep only string values and True boolean values
def keep_string_or_true(row):
    kept = {}
    for col, val in row.items():
        if pd.isna(val):
            continue
        if isinstance(val, str):
            if val.strip() != "":
                kept[col] = val
        elif val is True:
            kept[col] = val
    return json.dumps(kept)


def prepare_data(df, payload):
    # Prepare data for insertion
    points = []
    for idx, row in df.iterrows():
        point = PointStruct(
            id=idx,
            vector=row['embedding'],
            payload={
                "title": row[payload[0]],
                "description": row[payload[1]]
            }
        )
        points.append(point)
    return points


# Define collection
def define_collection(c, n, s):
    if not c.collection_exists(n):
        c.create_collection(
            collection_name=n,
            vectors_config=VectorParams(size=s, distance=Distance.COSINE)
        )


# Insert data into the collection
def insert_data(c, n, p):
    c.upsert(
        collection_name=n,
        points=p
    )


def db_init(collection_name, df, payload, vector_size):
    # Initialize Qdrant client
    # qdrant_client = QdrantClient(host="localhost", port=6333)
    qdrant_client = QdrantClient(":memory:")
    define_collection(qdrant_client, collection_name, vector_size)

    points = prepare_data(df, payload)
    insert_data(qdrant_client, collection_name, points)

    return qdrant_client



def read_csv_file(file_path):
    # Set pandas option to display full content of each cell
    pd.set_option('display.max_colwidth', None)

    # Load the CSV file into a DataFrame
    # the default file encoding type is 'utf_8', change to e.g. 'cp1252' if needed
    # the default field separator is ';', change to something else (e.g. ',') if needed
    df = filehandler.read_csv_file(file_path)

    drop_columns = ['shelflife', 'CN_code', 'country_of_origin']

    df_temp = df.copy()
    df_temp = df_temp.drop(columns=drop_columns)
    df_temp = df_temp.rename(columns={'product_name_alias': 'title', 'product_description': 'description'})

    # Add a column with per-row dict of kept values
    df_temp['json_data'] = df_temp.apply(keep_string_or_true, axis=1)

    keep_columns = ['title', 'description', 'json_data']
    df_temp = df_temp[keep_columns]

    return df_temp



def main(file_path='input/20251120-mfi-products.csv', payload=["title", "description"], model='mxbai-embed-large', collection_name='products_collection'):

    df_temp = read_csv_file(file_path)
    df_temp['embedding'] = df_temp['json_data'].apply(lambda x: generate_embeddings(x, m=model))

    measurer = np.vectorize(len)
    vector_size = measurer(df_temp['embedding']).max(axis=0)

    client = db_init(collection_name, df_temp, payload, vector_size)
    return client


if __name__ == "__main__":
    main()