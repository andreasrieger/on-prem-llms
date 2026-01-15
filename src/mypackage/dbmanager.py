# Storing vectors in Qdrant vector database

# pip install -qU langchain-qdrant

import sqlite3
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, database_exists
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams


_qdrant_client = None

# Initialize Qdrant client
def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        # _qdrant_client = QdrantClient(url="http://localhost:6333")
        _qdrant_client = QdrantClient(":memory:")
    return _qdrant_client


# Check if collection exists
def check_collection_exists(client, collection_name):
    return client.collection_exists(collection_name)


# Load the dataframe with embeddings
def store_vectors_in_qdrant(client, collection_name, df, payload):

    # Create collection if it doesn't exist
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

    # Prepare points to be uploaded
    points = []
    for idx, row in df.iterrows():
        point = PointStruct(
            id=idx,
            vector=row['embeddings'],
            payload = {
                "pl1": row[payload[0]],
                "pl2": row[payload[1]],
            }
        )
        points.append(point)

    # Upload points to Qdrant
    operation_info = get_qdrant_client().upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )

    return operation_info


def create_sqlite_engine(db_path):
    '''Function to create a SQLAlchemy engine for SQLite database'''
    return create_engine(f'sqlite+pysqlite:///{db_path}')


def get_sqlite_metadata(engine):
    '''Function to get metadata of the SQLite database'''
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return metadata


def check_table_exists(engine, table_name):
    '''Function to check if a table exists in the SQLite database'''
    metadata = get_sqlite_metadata(engine)
    return table_name in metadata.tables


# SQLite database functions
def write_df_to_sqlite(engine, df):
    '''Function to write a pandas DataFrame to an SQLite database'''
    return df.to_sql("products", con=engine, if_exists="replace", index=False)
