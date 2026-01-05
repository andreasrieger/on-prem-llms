import os, json
import pandas as pd
import numpy as np
from my_package import storage


def get_file_list(input_dir):
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def get_file_list_filtered(input_dir, file_extension):
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(file_extension.lower()):
                file_list.append(os.path.join(root, file))
    return file_list


def get_files_in_directory(input_dir, extensions=None):
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if extensions is None or any(file.lower().endswith(ext.lower()) for ext in extensions):
                file_list.append(os.path.join(root, file))
    return file_list


def print_enumerated_file_list(file_list):
    for idx, file_path in enumerate(file_list):
        print(f"{idx + 1}. {file_path}")


def get_file_path(input_dir, selected_file_num):
    file_list = get_file_list(input_dir)
    if selected_file_num.isdigit():
        index = int(selected_file_num) - 1
        if 0 <= index < len(file_list):
            return file_list[index]
    return selected_file_num  # Assume it's a direct file path


def read_csv_file(f, e='utf_8', s=';') -> pd.DataFrame:
    return pd.read_csv(f, encoding=e, sep=s)


def get_json_content(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


# Reading index.json and returning items from HUGO (SSG) site content
def process_hugo_index_json(index_json_path):
    site_content = get_json_content(str(index_json_path))
    data = json.loads(site_content)
    items = data.get('items', [])
    return items


def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


#@andreasrieger: Refactor to separate module
def process_markdown_files(input_dir):
    file_list = get_file_list_filtered(input_dir, '.md')
    for file_path in file_list:
        print(f"Found file: {file_path}")
        file_content = read_markdown_file(file_path)
        print(f"File content preview: {file_content[:200]}")  # Print first 100 characters of the file content
        db = storage.create_table()
        storage.write_db(db, file_path, "title", "content_date", file_content)


# Function to keep only string values and True boolean values
def keep_string_or_true(row):
    kept = {}
    for col, val in row.items():
        # print(f"col: {col}, val: {val} ({type(val)})")

        if pd.isna(val) or val is None:
            continue

        if isinstance(val, np.ndarray) and val.size < 1:
            continue

        if isinstance(val, np.ndarray) and val.size > 1:
            print(val)
            # kept[col] = val.any() # @andreasrieger: refactor to get clean array / list
            continue

        if isinstance(val, np.ndarray) and val.size > 0:
            kept[col] = val.tolist()


        if isinstance(val, str) and val.strip() != "":
            kept[col] = val.strip()


        if val is True:
            kept[col] = val

        # print(f"kept: {kept}")

    return json.dumps(kept)
