# Perform a search in the collection
def perform_search_in_qdrant(client, collection_name, query, limit=3):
    return client.query_points(
        collection_name=collection_name,
        query=query,
        with_vectors=True,
        with_payload=True,
        limit=limit,
    ).points


# Read data from SQLite database
def read_db(db):

    '''Function to read the database'''

    c = db.cursor()
    sql = '''
        SELECT * FROM site_content
    '''
    c.execute(sql)
    return c.fetchall()