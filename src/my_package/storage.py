# Storing vectors in Qdrant vector database

# pip install -qU langchain-qdrant

import sqlite3
from sqlalchemy import create_engine
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams


_qdrant_client = None

# Initialize Qdrant client
def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url="http://localhost:6333")
        # _qdrant_client = QdrantClient(":memory:")
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


# Perform a search in the collection
def perform_search_in_qdrant(client, collection_name, query, limit=3):
    return client.query_points(
        collection_name=collection_name,
        query=query,
        with_vectors=True,
        with_payload=True,
        limit=limit,
    ).points




# SQLite database functions
def write_df_to_sqlite(df):

    '''Function to write a pandas DataFrame to an SQLite database'''
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, future=True)
    res = df.to_sql("products", con=engine, if_exists="replace", index=False)
    return res


# Create table in SQLite database
def create_table():

    '''Function to create the database table if it does not exist'''

    db = sqlite3.connect('db.sqlite')
    c = db.cursor()
    c.execute('''
            CREATE TABLE if not exists site_content (
                  id INTEGER PRIMARY KEY,
                  file_name VARCHAR(30),
                  title TEXT,
                  content_date TEXT,
                  file_content TEXT
            );
    ''')
    db.commit()
    return db


# Write data to SQLite database
def write_db(db, file_name, title, content_date, file_content):

    '''Function to write data to database'''

    c = db.cursor()
    sql = '''
        INSERT INTO site_content(file_name, title, content_date, file_content)
        VALUES (?,?,?,?)
    '''
    c.execute(sql, (file_name, title, content_date, file_content))
    db.commit()


# Read data from SQLite database
def read_db(db):

    '''Function to read the database'''

    c = db.cursor()
    sql = '''
        SELECT * FROM site_content
    '''
    c.execute(sql)
    return c.fetchall()
