import os, json
import pandas as pd
import numpy as np


def get_file_list(input_dir):
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def get_file_list_filtered(input_dir, extensions):
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(extensions if isinstance(extensions, tuple) else (extensions.lower())):
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
        return read_markdown_file(file_path)



def get_file_content_dict(filehandler):
    file_content_dict = {}
    for page_num, page in enumerate(filehandler.pages):
        text = page.extract_text()
        file_content_dict[f"page_{page_num + 1}"] = text
    return file_content_dict


def get_file_content_list(filehandler) -> list:
    file_content_dict = {}
    file_content_list = []

    for page_num, page in enumerate(filehandler.pages):
        text = page.extract_text()
        file_content_dict = {
            "page_number": page_num + 1,
            "text": text
        }
        file_content_list.append(file_content_dict)
    return file_content_list


def read_pdf_file(file_path: str) -> list:

    # importing required classes
    from pypdf import PdfReader

    # creating a pdf reader object
    filehandler = PdfReader(file_path)

    # collecting all the text from the pdf file
    return get_file_content_list(filehandler)


def read_docx_file(file_path: str) -> str:
    # Placeholder for DOCX reading logic
    return "DOCX content reading not yet implemented."


def read_txt_file(file_path: str) -> str:
    # Placeholder for TXT reading logic
    return "TXT content reading not yet implemented."


def summarize_text_chunk(text_chunk: str, max_tokens: int = 100) -> str:
    # Placeholder for text summarization logic
    # In a real implementation, this could call an LLM or other summarization service
    summary = text_chunk[:max_tokens] + "..." if len(text_chunk) > max_tokens else text_chunk
    return summary


def process_document_files(input_dir) -> list:
    file_list = get_file_list_filtered(input_dir, ('.pdf', '.docx', '.txt'))
    for file_path in file_list:
        print(f"Processing file: {file_path}")
        # Here you can add code to read and process the document files as needed
        # For example, extract text from PDFs or Word documents
        # This is a placeholder for actual document processing logic
        file_content = read_pdf_file(file_path) if file_path.lower().endswith('.pdf') else \
                       read_docx_file(file_path) if file_path.lower().endswith('.docx') else \
                       read_txt_file(file_path)
        return file_content


def process_pdf_file(file_path: str) -> list:
    return read_pdf_file(file_path)


# Function to reorder DataFrame columns
def reorder_dataframe_columns(dataframe, cols_to_move):
    cols = list(dataframe.columns)
    for col in cols_to_move:
        if col in cols:
            cols.insert(cols_to_move.index(col), cols.pop(cols.index(col)))
    return dataframe[cols]


# Function to keep only string values and True boolean values
def keep_string_or_true(row):
    kept = {}
    for col, val in row.items():

        if pd.isna(val) or val is None:
            continue

        if isinstance(val, np.ndarray) and val.size < 1:
            continue

        if isinstance(val, np.ndarray) and val.size > 1:
            print(val)
            continue

        if isinstance(val, np.ndarray) and val.size > 0:
            kept[col] = val.tolist()


        if isinstance(val, str) and val.strip() != "":
            kept[col] = val.strip()


        if val is True:
            kept[col] = val

    return json.dumps(kept)
