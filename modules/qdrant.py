# Storing vectors in Qdrant vector database

# pip install -qU langchain-qdrant

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
# from ast import literal_eval
# from langchain_qdrant import QdrantVectorStore


# Initialize Qdrant client
# qdrant_client = QdrantClient(host="localhost", port=6333)
qdrant_client = QdrantClient(":memory:")


# Load the dataframe with embeddings
def store_vectors_in_qdrant(df, collection_name, payload):

    # Create collection if it doesn't exist
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=len(df['embedding'].iloc[0]), distance=Distance.COSINE)
        )

    # Prepare points to be uploaded
    points = []

    for idx, row in df.iterrows():
        point = PointStruct(
            id=idx,
            vector=row['embedding'],
            payload = {
                "pl1": row[payload[0]],
                "pl2": row[payload[1]],
            }
        )
        points.append(point)

    # Upload points to Qdrant
    operation_info = qdrant_client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )

    # return f"Stored {len(points)} vectors in Qdrant collection '{collection_name}'."
    return operation_info


# Perform a search in the collection
def perform_search_in_qdrant(query, collection_name, payload, limit=3):
    return qdrant_client.query_points(
        collection_name=collection_name,
        query=query,
        with_vectors=True,
        with_payload=[payload[0], payload[1]],
        limit=limit,
    ).points