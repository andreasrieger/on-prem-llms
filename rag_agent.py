import os
from typing import Any, Sequence
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_qdrant import QdrantVectorStore
from sqlalchemy import create_engine, MetaData, Table, select, Row
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from mypackage import finder, userinput
from langchain.tools import tool
from langchain.agents import create_agent
from uuid import uuid4


def get_chunks_from_db() -> Sequence[Row[Any]]:
    """
    Retrieve all document chunks from the SQLite database.

    Returns:
        Sequence[Row[Any]]: A sequence of database rows containing document chunks.
            Each row includes page_num, chunk_num, content, and source.
    """
    data_dir = os.path.join(finder.get_git_root(), "data")
    db_name = 'documents.db'
    db_path = os.path.join(data_dir, db_name)

    engine = create_engine(f"sqlite:////{db_path}")

    metadata = MetaData()

    table = Table(
        'documents',
        metadata,
        autoload_with=engine
    )

    stmt = select(table)
    connection = engine.connect()

    results: Sequence[Row[Any]] = connection.execute(stmt).fetchall()
    # for row in results:
    #     print(row)
    return results


def get_use_cases():
    """
    Get available use cases for the RAG system.

    Returns:
        list: A list of strings describing available use cases.
    """
    return [
        "Retrieve from existing database",
        "Update database with own data"
    ]


def store_vectors_in_qdrant(documents) -> QdrantVectorStore:
    """
    Store document embeddings in an in-memory Qdrant vector database.

    Args:
        documents: A sequence of Document objects to be embedded and stored.

    Returns:
        QdrantVectorStore: The configured vector store containing the embedded documents.
    """
    collection_name = "documents_collection"
    embeddings = OllamaEmbeddings(model='nomic-embed-text', validate_model_on_init=True)

    client: QdrantClient = QdrantClient(":memory:")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )

    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)

    return vector_store


def get_document_list(chunks):
    """
    Convert database chunk rows into LangChain Document objects.

    Args:
        chunks: A sequence of database rows containing chunk data.
            Each row should have: (page_num, chunk_num, content, source).

    Returns:
        list: A list of Document objects with content and metadata.
    """
    docs = list()
    for chunk in chunks:
        metadata = {"source": chunk[3], "page_num": chunk[0], "chunk_num": chunk[1]}
        docs.append(Document(page_content=chunk[2], metadata=metadata))
    return docs


def main():
    """
    Initialize and run the RAG (Retrieval-Augmented Generation) agent.

    This function sets up the complete RAG pipeline:
    - Loads document chunks from the database
    - Creates embeddings and stores them in Qdrant
    - Configures a LangChain agent with retrieval tools
    - Runs an interactive chat loop for user queries
    """
    print("Starting RAG agent...")

    chunks = get_chunks_from_db()
    documents = get_document_list(chunks)
    vector_store = store_vectors_in_qdrant(documents)


    @tool(response_format="content_and_artifact")
    def retrieve_context(query: str):
        """Retrieve information to help answer a query."""
        retrieved_docs = vector_store.similarity_search(query, k=2)
        serialized = "\n\n".join(
            f"Source: {doc.metadata}\nContent: {doc.page_content}"
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs


    tools = [retrieve_context]

    prompt = (
        "You have access to a tool that retrieves context from a document. Use the tool to help answer user queries and refer to a part and a page in the document when answering."
    )

    model = ChatOllama(
        model="ministral-3",
        validate_model_on_init=True,
        temperature=0.0,
    )

    agent = create_agent(model, tools, system_prompt=prompt)

    # Initialize chatbot
    exit_conditions = (":q", "quit", "exit")
    while True:
        # Get user query
        user_query = userinput.get_user_input("Post your question! (Or quit with ':q')", default="What is the document about?")
        if user_query in exit_conditions:
            break
        else:
            query_str = {"query": {"type": "string", "value": user_query}}
            input = {"messages": [{"role": "user", "content": str(query_str)}]}
            for event in agent.stream(input=input, stream_mode="values"):
                event["messages"][-1].pretty_print()



if __name__ == "__main__":
    main()