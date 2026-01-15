import json
import pandas as pd
import numpy as np
from collections.abc import Iterable


def f(v):
    if isinstance(v, tuple):
        return v[0]
    return v


def get_column_info(df, column):
    column_info = {}
    column_info['dtype'] = str(df[column].dtype),
    column_info["non_null_count"] = int(df[column].count()),
    column_info["null_count"] = int(df[column].isnull().sum()),
    column_info["unique_values"] = df[column].explode().nunique(),
    column_info["sample_values"] = df[column].dropna().unique()[:5].tolist(),
    column_info["statistics"] = df[column].describe().to_dict() if pd.api.types.is_numeric_dtype(df[column]) else None
    return {k: f(v) for k, v in column_info.items() if isinstance(v, Iterable)}


def write_knowledge_to_file(knowledge, filename="knowledge.json"):
    with open(filename, "w") as f:
        f.write(knowledge)
        f.close()


def read_knowledge_from_file(filename="knowledge.json"):
    # Read and pretty-print the knowledge JSON file
    with open(filename, "r") as f:
        parsed = json.load(f)
        f.close()
    return json.dumps(parsed, indent=4)


def convert_pd_object_values_to_str(df):
    object_columns = df.select_dtypes(include=['object']).columns.tolist()
    if len(object_columns) > 0:
        df[object_columns] = df[object_columns].astype('string')
    return df


def generate_knowledge(df):
    # Convert object columns to string type
    df = convert_pd_object_values_to_str(df)

    # Create knowledge dictionary with table schema information
    knowledge = {}
    knowledge["object_type"] = "table"
    knowledge["table_name"] = "products"

    # Generate schema information in JSON format and add to knowledge
    schema_info = {}
    for column in df.columns:
        schema_info[column] = get_column_info(df, column)

    knowledge["schema"] = schema_info

    # Get sample rows from the DataFrame and add to knowledge
    sample_rows = df.sample(2, random_state=1)

    knowledge["sample_rows"] = sample_rows.to_dict(orient="records")

    knowledge_json = json.dumps(knowledge, indent=4)
    write_knowledge_to_file(knowledge_json)
    return knowledge_json


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