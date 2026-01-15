from mypackage import embedder


def get_nice_strings(lst):
    return [lst.strip().replace('\n ', '').replace('\n', '').lower() for lst in lst]


def get_nice_string(s):
    return s.strip().replace('\n ', '').replace('\n', '').lower()


def get_db_ready_column_names(lst):
    lst = get_nice_strings(lst)
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


# Convert each row of the DataFrame to a JSON string
def add_json_data_column(df):
    df['json_data'] = df.apply(lambda row: row.to_json(), axis=1)
    return df


def add_vectorized_column(df):
    df['embedding'] = df.apply(lambda row: embedder.get_embedding(row['json_data']), axis=1)
    return df