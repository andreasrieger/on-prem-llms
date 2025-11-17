import json
import pandas as pd
from collections.abc import Iterable


def f(v):
    if isinstance(v, tuple):
        return str(v[0])
    return v


def get_column_info(df, column):
    # return df[column].explode().nunique()
    column_info = {}
    column_info["dtype"] = df[column].dtype,
    column_info["non_null_count"] = df[column].count(),
    column_info["null_count"] = df[column].isnull().sum(),
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
    with open("knowledge.json", "r") as f:
        parsed = json.load(f)
        f.close()
    return json.dumps(parsed, indent=4)


def generate_knowledge(df):
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
