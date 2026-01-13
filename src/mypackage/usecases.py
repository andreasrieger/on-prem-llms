import locale, os
import pandas as pd
import numpy as np
from mypackage import datapreparation, docroot, userinput, filemanager, ospath, chunking, embedding, storage


# use German locale; name and availability varies with platform
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, '')

# Cache for Git root directory
_git_root = docroot.get_git_root()

# Input directory
_input_dir = docroot.get_input_dir() + os.sep
# _input_dir = ospath.get_download_folder() # Default to Downloads folder


# Output directory
_output_dir = docroot.get_output_dir() + os.sep

# Data directory
_data_dir = docroot.get_data_dir() + os.sep

# Define available use cases
def get_use_cases():
    use_cases = [
        {   # Document Indexing and Search
            "id": 0,
            "name": "Document Indexing and Search",
            "collection_name": "documents_collection",
            "payload": ['page_number', 'chapter_summary']
        },
        {   # Data Table Indexing and Search
            "id": 1,
            "name": "Data Table Indexing and Search",
            "collection_name": "products_collection",
            "payload": ['product_name_alias', 'product_description']
        }
    ]
    return use_cases


# Print enumerated use cases list
def print_enumerated_use_cases_list(use_cases):
    print("Available Use Cases:")
    for idx, use_case in enumerate(use_cases):
        print(f"{idx + 1}. {use_case['name']}")


# Initialize the selected use case
def init_use_case(use_case, client, db_init=True):
    match use_case:
        case 0:
            return doc_indexing_and_search(0, client, db_init=db_init)
        case 1:
            return data_table_indexing_and_search(1, client, db_init=db_init)
        case 2:
            return hugo_content_indexing_and_search(2, client, db_init=db_init)
        case _:
            print(f"Invalid use case: {use_case}")
            return None


# Use case implementation: Document Indexing and Search
def doc_indexing_and_search(use_case, client, db_init):

    print("Starting Document Indexing and Search use case...")

    pd.set_option('display.max_colwidth', None)
    pd.set_option("mode.copy_on_write", True) # see: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-chained-assignment

    # Create a collection
    collection_name = get_use_cases()[use_case]['collection_name']

    # Define payload for vector storage
    payload = get_use_cases()[use_case]['payload']

    # Get input directory from user
    input_dir = userinput.get_user_input("Input directory", default=f"{_input_dir}")

    # List files in the input directory
    file_list = filemanager.get_files_in_directory(input_dir, extensions=[".pdf"])
    filemanager.print_enumerated_file_list(file_list)

    # Get selected file from user
    selected_file_num = userinput.get_user_input("Select a file by number", default="1")
    selected_file_path = file_list[int(selected_file_num) - 1]

    # Process document file
    file_content = filemanager.read_pdf_file(selected_file_path)

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(file_content)

    # Further processing, embedding generation, and storage logic would go here
    # chunking and chunk enrichment
    list_of_chunks = list(zip(df['page_number'], df['text'].apply(lambda x: chunking.text_chunking(x, chunk_size=512))))
    df_chunks = pd.DataFrame(list_of_chunks, columns=['page_number', 'chunks'])
    df_chunks = df_chunks.explode('chunks').dropna(subset=['chunks'])
    df_chunks['cleaned_chunks'] = df_chunks['chunks'].apply(lambda x: x.lower().replace('-\n', '').replace('\n', ' ').strip())
    df_chunks['chapter_summary'] = df_chunks['cleaned_chunks'].apply(lambda x: filemanager.summarize_text_chunk(x, max_tokens=100))

    # Reordering columns into desired order
    cols_to_move = ['page_number', 'chapter_summary', 'cleaned_chunks']
    df_chunks = filemanager.reorder_dataframe_columns(df_chunks, cols_to_move)

    # Exporting chunks to output file
    df_chunks.to_csv(_output_dir + "document_chunks.csv", index=False)

    # generating embeddings (vectors) for the chunks
    df_chunks['embeddings'] = df_chunks['cleaned_chunks'].apply(lambda x: embedding.get_embedding(x, model='mxbai-embed-large'))

    if db_init:
        # storing vectors in Qdrant
        return storage.store_vectors_in_qdrant(client, collection_name, df_chunks, payload)
    else:
        return df_chunks.to_dict(orient='records')


# Use case implementation: Data Table Indexing and Search
def data_table_indexing_and_search(use_case, client, db_init):

    pd.set_option('display.max_colwidth', None)
    pd.set_option("mode.copy_on_write", True) # see: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-chained-assignment

    # Create a collection
    collection_name = get_use_cases()[use_case]['collection_name']

    # Define payload for vector storage
    payload = get_use_cases()[use_case]['payload']

    # Get input directory from user
    input_dir = userinput.get_user_input("Input directory", default=_input_dir)

    # List files in the input directory
    file_list = filemanager.get_files_in_directory(input_dir, extensions=[".xlsx", ".xls"])
    filemanager.print_enumerated_file_list(file_list)

    # Get selected file from user
    selected_file_num = userinput.get_user_input("Select a file by number", default="1")
    selected_file_path = file_list[int(selected_file_num) - 1]

    # Read and reshape the selected Excel file
    df = datapreparation.get_reshaped_dataframe(selected_file_path)

    # Reordering columns to have 'product_name_alias' first if it exists
    cols_to_move = ['product_name_alias', 'fat_content_minimum%', 'fat_content_maximum%', 'protein_content_minimum%', 'protein_content_maximum%']
    df = filemanager.reorder_dataframe_columns(df, cols_to_move)

    # Export dataframe to Excel, CSV and JSON
    # df.to_excel(_output_dir + "product_data.xlsx", index=False)
    # df.to_csv(_output_dir + "product_data.csv", index=False)
    # df.to_json(_output_dir + "product_data.json", orient='records')

    # create json from available data
    df['json_data'] = df.apply(lambda x: x.to_dict() if x.notna().any() else None, axis=1)

    # generating embeddings (vectors) for the json data
    df['embeddings'] = df['json_data'].apply(lambda x: embedding.get_embedding(str(x), model='mxbai-embed-large') if x is not None else None)

    if db_init:
        # Store vectors in Qdrant
        return storage.store_vectors_in_qdrant(client, collection_name, df, payload)
    else:
        return "Data saved to output file."


# Use case implementation: Content Indexing and Search from HUGO site (works only in HUGO context)
def hugo_content_indexing_and_search(use_case, client, db_init):

    pd.set_option('display.max_colwidth', None)
    pd.set_option("mode.copy_on_write", True) # see: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-chained-assignment

    # Create a collection
    collection_name = get_use_cases()[use_case]['collection_name']

    # Define payload for vector storage
    payload = get_use_cases()[use_case]['payload']

    # Get input directory from user
    # _input_dir = userinput.get_user_input("Input directory", default=ospath.get_download_folder())
    input_dir = userinput.get_user_input("HUGO public files directory", default='../public')

    # List files in the input directory
    file_list = filemanager.get_file_list(input_dir)
    filemanager.print_enumerated_file_list(file_list)

    # Get selected file from user
    selected_file_num = userinput.get_user_input("Enter number of index file from the list above", default=f"{input_dir}/index.json")
    selected_file_path = filemanager.get_file_path(input_dir, selected_file_num)
    print(f"Selected file: {selected_file_path}")

    # Read and process HUGO index.json file
    items = filemanager.process_hugo_index_json(selected_file_path)
    df = pd.DataFrame.from_dict(items)

    # chunking and chunk enrichment
    list_of_chunks = list(zip(df['url'], df['title'], df['content_text'].apply(lambda x: chunking.text_chunking(x, chunk_size=512))))
    df_chunks = pd.DataFrame(list_of_chunks, columns=['url', 'title', 'chunks'])
    df_chunks = df_chunks.explode('chunks').dropna(subset=['chunks'])
    df_chunks['cleaned_chunks'] = df_chunks['chunks'].apply(lambda x: x.lower().replace('\n', ' ').strip())

    # generating embeddings (vectors) for the chunks
    df_chunks['embeddings'] = df_chunks['cleaned_chunks'].apply(lambda x: embedding.get_embedding(x, model='mxbai-embed-large'))

    # Exporting chunks to output file
    df_chunks.to_csv(_output_dir + "content_chunks.csv", index=False)

    if db_init:
        # storing vectors in Qdrant
        return storage.store_vectors_in_qdrant(client, collection_name, df_chunks, payload)
    else:
        return "Contents saved to output file."


def main():

    # Set use case
    use_cases = get_use_cases()
    print_enumerated_use_cases_list(use_cases)
    selected_usecase = userinput.get_user_input("Select use case by number", default="1")
    selected_usecase = get_use_cases()[int(selected_usecase) - 1]
    print(f"Selected use case: {selected_usecase["name"]}")

    # Initialize Qdrant client
    client = storage.get_qdrant_client()

    # Perform the selected use case
    operation_info = init_use_case(selected_usecase["id"], client, db_init=False)
    print(f"Data stored. Operation Info: {operation_info}")


if __name__ == "__main__":
    main()