import pandas as pd


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


# DEPRECATED: Function to reshape dataframe with multi-level columns
def get_reshaped_dataframe(dataframe):

    # print(f"Processing file: {file_path}")

    # # creating an empty dataframe
    df = pd.DataFrame()

    # # reading the excel file with multi-level columns
    # df_i = pd.read_excel(file_path, header=[0,1])
    df_i = dataframe.copy()

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
            df_temp[new_colname] = df_temp.apply(lambda x: (x.dropna().to_numpy() if x.notna().any() else None), axis=1)

            # adding the new column to the main dataframe
            df[new_colname] = df_temp.loc[:, new_colname]

        else:
            # single column, just rename and add to main dataframe
            df[new_colname] = df_i.loc[:, col]

    # returning the reshaped dataframe
    return df

