from qdrant_client import QdrantClient
from mypackage import userinput



def delete_collection(client, collection_name):
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
        print(f"Collection '{collection_name}' deleted successfully.")


def get_collection_list(client):
    return client.get_collections().collections


def get_enumerated_list(lst):
    for idx, item in enumerate(lst):
        print(f"{idx + 1}. {item}")


def main():

    # Initialize Qdrant client
    client = QdrantClient(url="http://localhost:6333")
    collection_list = get_collection_list(client)
    get_enumerated_list(collection_list)

    selected_collection = userinput.get_user_input("Select collection by number")
    print(f"Selected collection: {selected_collection}")

    """
    selected_collection = collection_list[int(selected_collection) - 1]

    delete_collection(client, selected_collection)
    """


if __name__ == "__main__":
    main()



