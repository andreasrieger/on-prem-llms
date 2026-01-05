import locale, json
import os
import git
import pandas as pd
import numpy as np
from mypackage import userinput, filemanager, ospath, chunking, embedding, storage


_git_root = None

def get_git_root(path):
    global _git_root
    if _git_root is None:
        git_repo = git.Repo(path, search_parent_directories=True)
        git_root = git_repo.git.rev_parse("--show-toplevel")
        _git_root = git_root
    return _git_root

# use German locale; name and availability varies with platform
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, '')

# Root directory of the package
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_use_cases():
    use_cases = [
        {
            # HUGO Content Indexing and Search
            "id": 0,
            "name": "HUGO Content Indexing and Search",
            "collection_name": "content_collection",
            "payload": ['url', 'title']
        },{
            # Data Table Indexing and Search
            "id": 1,
            "name": "Data Table Indexing and Search",
            "collection_name": "products_collection",
            "payload": ['product_name_alias', 'product_description']
        },{
            # Document Indexing and Search
            "id": 2,
            "name": "Document Indexing and Search",
            "collection_name": "documents_collection",
            "payload": ['page_number', 'chapter_summary']
        }
    ]
    return use_cases


def print_enumerated_use_cases_list(use_cases):
    print("Available Use Cases:")
    for idx, use_case in enumerate(use_cases):
        print(f"{idx + 1}. {use_case['name']}")


def init_use_case(use_case, client, db_init=True):
    match use_case:
        case 0:
            return hugo_content_indexing_and_search(0, client, db_init=db_init)
        case 1:
            return data_table_indexing_and_search(1, client, db_init=db_init)
        case 2:
            return doc_indexing_and_search(2, client, db_init=db_init)
        case _:
            print(f"Invalid use case: {use_case}")
            return None


def get_nice_strings(lst):
    return [lst.strip().replace('\n ', '').replace('\n', '').lower() for lst in lst]


def get_nice_string(s):
    return s.strip().replace('\n ', '').replace('\n', '').lower()


def get_nice_column_names(lst):
    return [lst.replace(' ', '_').lower() for lst in lst]


def get_duplicate_column_names(dataframe, level=0):
    # declaring a set for duplicated column names
    dupcols_set = set()

    # collecting column names in given level
    colnames = dataframe.columns.get_level_values(level)

    return list({x for x in colnames if x in dupcols_set or dupcols_set.add(x)})


def get_unique_column_names(dataframe, level=0):
    cols = dataframe.columns.get_level_values(level)
    return list(set(cols))


# Function to reshape dataframe with multi-level columns
def get_reshaped_dataframe(file_path):

    # creating an empty dataframe
    df = pd.DataFrame()

    # reading the excel file with multi-level columns
    df_i = pd.read_excel(file_path, header=[0,1])

    # getting column names at level 0 and identifying duplicates
    dupcols = get_duplicate_column_names(df_i, level=0)

    # iterating through unique columns
    unique_cols = get_unique_column_names(df_i, level=0)

    for col in unique_cols:

        # creating new column name
        new_colname = get_nice_string(col).replace(' ', '_')

        if (col in dupcols):

            # create temporary dataframe with only the duplicated columns
            df_temp = df_i.xs(col, level=0, axis=1, drop_level=False)

            # getting column names from level 1
            colnames = df_temp.columns.get_level_values(1)

            # cleaning and replacing column names
            temp_colnames = get_nice_strings(colnames)
            df_temp.columns = temp_colnames[:]

            # replacing 'x' in dataframe with column names
            df_temp.replace('x', pd.Series(df_temp.columns, df_temp.columns), inplace=True)

            # updating column names again after replacement
            df_temp.columns = get_nice_column_names(temp_colnames)[:]

            # combining multiple columns into a list, ignoring NaN values
            df_temp[new_colname] = df_temp.apply(lambda x: (list(x.dropna().to_numpy()) if x.notna().any() else None), axis=1)

            # adding the new column to the main dataframe
            df[new_colname] = df_temp.loc[:, new_colname]

        else:
            # single column, just rename and add to main dataframe
            df[new_colname] = df_i.loc[:, col]

    # Reordering columns to have 'product_name_alias' first if it exists
    cols = list(df)
    cols_to_move = ['product_name_alias', 'fat_content_minimum%', 'fat_content_maximum%', 'protein_content_minimum%', 'protein_content_maximum%']
    if 'product_name_alias' in df.columns:
        for col in cols_to_move:
            cols.insert(cols.index(col), cols.pop(cols.index(col)))
            df = df.loc[:, cols]

    # returning the reshaped dataframe
    return df


# Use case implementations
def doc_indexing_and_search(use_case, client, db_init):

    print("Starting Document Indexing and Search use case...")

    pd.set_option('display.max_colwidth', None)
    pd.set_option("mode.copy_on_write", True) # see: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-chained-assignment

    # Create a collection
    collection_name = get_use_cases()[use_case]['collection_name']

    # Define payload for vector storage
    payload = get_use_cases()[use_case]['payload']

    # Get input directory from user
    input_dir = userinput.get_user_input("Input directory", default=f'{_git_root}/input/documents')

    # Process document files
    file_content = filemanager.process_document_files(input_dir)
    # print(f"File content: {file_content}")


    # Convert to DataFrame for easier handling
    df = pd.DataFrame(file_content)

    # Further processing, embedding generation, and storage logic would go here
    # chunking and chunk enrichment
    list_of_chunks = list(zip(df['page_number'], df['text'].apply(lambda x: chunking.text_chunking(x, chunk_size=512))))
    df_chunks = pd.DataFrame(list_of_chunks, columns=['page_number', 'chunks'])
    df_chunks = df_chunks.explode('chunks').dropna(subset=['chunks'])
    df_chunks['cleaned_chunks'] = df_chunks['chunks'].apply(lambda x: x.lower().replace('\n', ' ').strip())
    # print(df_chunks.head(-3))

    df_chunks['chapter_summary'] = df_chunks['cleaned_chunks'].apply(lambda x: filemanager.summarize_text_chunk(x, max_tokens=100))

    # generating embeddings (vectors) for the chunks
    df_chunks['embeddings'] = df_chunks['cleaned_chunks'].apply(lambda x: embedding.get_embedding(x, model='mxbai-embed-large'))
    # print(df_chunks.head(-3))

    # Exporting chunks to output file
    output_dir = f"{_git_root}/output/"
    df_chunks.to_csv(output_dir + "document_chunks.csv", index=False)

    if db_init:
        # storing vectors in Qdrant
        return storage.store_vectors_in_qdrant(client, collection_name, df_chunks, payload)
    else:
        return "Contents saved to output file."








# Use case implementations
def hugo_content_indexing_and_search(use_case, client, db_init):

    pd.set_option('display.max_colwidth', None)
    pd.set_option("mode.copy_on_write", True) # see: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-chained-assignment

    # Create a collection
    collection_name = get_use_cases()[use_case]['collection_name']

    # Define payload for vector storage
    payload = get_use_cases()[use_case]['payload']

    # Get input directory from user
    # input_dir = userinput.get_user_input("Input directory", default=ospath.get_download_folder())
    input_dir = userinput.get_user_input("HUGO public files directory", default='../public')

    # List files in the input directory
    file_list = filemanager.get_file_list(input_dir)
    filemanager.print_enumerated_file_list(file_list)

    # Get selected file from user
    selected_file_num = userinput.get_user_input("Enter number of index file from the list above", default=f"{input_dir}/index.json")
    selected_file_path = filemanager.get_file_path(input_dir, selected_file_num)
    print(f"Selected file: {selected_file_path}")

    items = filemanager.process_hugo_index_json(selected_file_path)
    df = pd.DataFrame.from_dict(items)

    # chunking and chunk enrichment
    list_of_chunks = list(zip(df['url'], df['title'], df['content_text'].apply(lambda x: chunking.text_chunking(x, chunk_size=512))))
    df_chunks = pd.DataFrame(list_of_chunks, columns=['url', 'title', 'chunks'])
    df_chunks = df_chunks.explode('chunks').dropna(subset=['chunks'])
    df_chunks['cleaned_chunks'] = df_chunks['chunks'].apply(lambda x: x.lower().replace('\n', ' ').strip())

    # generating embeddings (vectors) for the chunks
    df_chunks['embeddings'] = df_chunks['cleaned_chunks'].apply(lambda x: embedding.get_embedding(x, model='mxbai-embed-large'))
    # return df_chunks.head().to_dict()

    # Exporting chunks to output file
    output_dir = f"{_git_root}/output/"
    df_chunks.to_csv(output_dir + "content_chunks.csv", index=False)

    if db_init:
        # storing vectors in Qdrant
        return storage.store_vectors_in_qdrant(client, collection_name, df_chunks, payload)
    else:
        return "Contents saved to output file."


def data_table_indexing_and_search(use_case, client, db_init):

    pd.set_option('display.max_colwidth', None)
    pd.set_option("mode.copy_on_write", True) # see: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-chained-assignment

    # Create a collection
    collection_name = get_use_cases()[use_case]['collection_name']

    # Define payload for vector storage
    payload = get_use_cases()[use_case]['payload']

    output_dir = "../../output/"

    # Get input directory from user
    input_dir = userinput.get_user_input("Input directory", default=ospath.get_download_folder()) # deactivated for testing

    # List files in the input directory
    file_list = filemanager.get_files_in_directory(input_dir, extensions=[".xlsx", ".xls"])
    filemanager.print_enumerated_file_list(file_list)

    selected_file_num = userinput.get_user_input("Select a file by number", default="1")
    selected_file_path = file_list[int(selected_file_num) - 1]
    print(f"Selected file: {selected_file_path}")
    df = get_reshaped_dataframe(selected_file_path)

    # Export dataframe to Excel, CSV and JSON
    df.to_excel(output_dir + "product_data.xlsx", index=False)
    df.to_csv(output_dir + "product_data.csv", index=False)
    df.to_json(output_dir + "product_data.json", orient='records')

    # create json from available data
    df['json_data'] = df.apply(lambda x: x.to_dict() if x.notna().any() else None, axis=1)


    # Option A: keep the dicts (one cell per row)
    # filtered_series = df_temp['filtered']

    # Option B: expand dicts back to columns (sparse; missing entries become NaN)
    # filtered_df = pd.json_normalize(filtered_series).reindex(df_temp.index)

    # If you want df_temp to be the expanded result uncomment:
    # df_temp = filtered_df

    df['embeddings'] = df['json_data'].apply(lambda x: embedding.get_embedding(str(x), model='mxbai-embed-large') if x is not None else None)

    if db_init:
        # Store vectors in Qdrant
        return storage.store_vectors_in_qdrant(client, collection_name, df, payload)
    else:
        return "Data saved to output file."


def main():
    # Set use case
    use_cases = get_use_cases()
    print_enumerated_use_cases_list(use_cases)
    selected_usecase = userinput.get_user_input("Select use case by number", default="3")
    selected_usecase = get_use_cases()[int(selected_usecase) - 1]
    print(f"Selected use case: {selected_usecase["name"]}")

    # Initialize Qdrant client
    client = storage.get_qdrant_client()

    # Perform the selected use case
    operation_info = init_use_case(selected_usecase["id"], client, db_init=False)
    print(f"Data stored. Operation Info: {operation_info}")


if __name__ == "__main__":
    get_git_root(os.path.dirname(os.path.abspath(__file__)))
    main()