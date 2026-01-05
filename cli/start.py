from my_package import usecases, filemanager, storage, userinput, embedding

# !{sys.executable} -m pip install qdrant-client ollama sqlalchemy langchain-text-splitter


# Get user input
def get_user_query():
    # Get and validate user input
    qry = userinput.get_user_input("Enter search term")
    if userinput.validate_search_term(qry):
        # Proceed with search
        pass
    return qry


# Perform search in Qdrant
def search(client, query, collection_name, limit=3):
    return storage.perform_search_in_qdrant(
        client = client,
        query = query,
        collection_name = collection_name,
        limit = limit
    )


def print_search_results(results):
    for idx, result in enumerate(results):
        print(f"Result {idx + 1}:")
        print(f"ID: {result.id}")
        print(f"Score: {result.score}")
        print("Payload:")
        for key, value in result.payload.items():
            print(f"  {key}: {value}")
        print("-" * 20)


#@andreasrieger: Caching search results can be implemented here
def main():

    # Set use case
    use_cases = usecases.get_use_cases()
    usecases.print_enumerated_use_cases_list(use_cases)
    selected_usecase = userinput.get_user_input("Select use case by number", default="1")
    selected_usecase = usecases.get_use_cases()[int(selected_usecase) - 1]
    print(f"Selected use case: {selected_usecase["name"]}")

    # Set collection_name according to selected use case
    collection_name = selected_usecase["collection_name"]

    # Initialize Qdrant client
    client = storage.get_qdrant_client()



    # Initialize Qdrant client
    init_search = storage.check_collection_exists(client, collection_name)

    if not init_search:
        print(f"Collection '{collection_name}' does not exist. Setting up collection...")

        # Perform the selected use case
        operation_info = usecases.init_use_case(selected_usecase["id"], client)
        print(f"Data stored. Operation Info: {operation_info}")
    else:
        print(f"Collection '{collection_name}' exists. Proceeding to search...")



    # Get user input
    query = get_user_query()

    # Get embedding for the query
    query_embedding = embedding.get_embedding(query)

    # Perform search
    results = search(client, query_embedding, collection_name, limit=3)

    # Print results
    print_search_results(results)
    print("\n" * 3)


if __name__ == "__main__":
    main()
