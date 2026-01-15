import os
import pandas as pd
from mypackage import finder, preparator, userinput
from sqlalchemy import String, Table, Column, Integer, String, Float, Boolean, create_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column

pd.set_option('display.max_colwidth', None)
pd.set_option("mode.copy_on_write", True) # see: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-chained-assignment
pd.set_option('future.no_silent_downcasting', True)


# Creating Base class for database setup
class Base(DeclarativeBase):
    pass


# Storing dataframe to products database
def store_dataframe_to_db(df):

    data_dir = os.path.join(finder.get_git_root(), "data")
    db_name = 'products.db'
    db_path = os.path.join(data_dir, db_name)

    engine = create_engine(f"sqlite:////{db_path}")

    Base.metadata.create_all(engine)

    products_table = Table(
        "products",
        Base.metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("product_name_alias", String),
        Column("fat_content_minimum%", Float),
        Column("fat_content_maximum%", Float),
        Column("protein_content_minimum%", Float),
        Column("protein_content_maximum%", Float),
        Column("dairy", Boolean),
        Column("bakery_&_sweets", Boolean),
        Column("nutrition", Boolean),
        Column("savoury", Boolean),
        Column("single_ingredients", Boolean),
        Column("vegetarian", Boolean),
        Column("vegan", Boolean),
        Column("non-added_sugar", Boolean),
        Column("lactose_free", Boolean),
        Column("gluten_free", Boolean),
        Column("palm", Boolean),
        Column("coconut", Boolean),
        Column("sunflower", Boolean),
        Column("kosher", Boolean),
        Column("super_kosher", Boolean),
        Column("halal", Boolean),
        Column("vlog", Boolean),
        Column("rspo_mb", Boolean),
        Column("rspo_sg", Boolean),
        Column("palmfree", Boolean),
        Column("clean_label", Boolean),
        Column("acid_stable", Boolean),
        Column("product_description", String),
        Column("yoghurt_&_sour_milk_products", Boolean),
        Column("cream_cheese", Boolean),
        Column("processed_cheese", Boolean),
        Column("milk_based_beverages", Boolean),
        Column("cake_filling_&_decoration_creme", Boolean),
        Column("emulsifiers_for_pastry_products", Boolean),
        Column("egg_substitution_and_egg_reduction", Boolean),
        Column("glazing_agents", Boolean),
        Column("cold-cream_and_custard_cream", Boolean),
        Column("ice_cream", Boolean),
        Column("hot_beverages", Boolean),
        Column("energy_bars", Boolean),
        Column("protein_enriched_dairy_products", Boolean),
        Column("sports_nutrition", Boolean),
        Column("protein_shakes", Boolean),
        Column("nutritional_meals", Boolean),
        Column("cooked,_scalded_and_raw_sausage", Boolean),
        Column("processed_meat_products", Boolean),
        Column("cooked_ham", Boolean),
        Column("soups_and_sauces", Boolean),
        Column("dressings_and_mayonnaises", Boolean),
        Column("meggle´s_corresponding_product_family", String), # wrong character
        Column("hydrogenated", Boolean),
        Column("non_hydrogenated", Boolean),
        Column("product_family", String),
        Column("product_group", String),
    )

    # df.to_sql('products', con=engine, if_exists='replace')
    return df.to_sql(products_table.name, index=False, con=engine, if_exists='replace')


# Function to reshape dataframe with multi-level columns
def get_reshaped_dataframe(dataframe):
    df = dataframe.copy()

    # getting column names at level 0 and identifying duplicates
    dupcols = preparator.get_duplicate_column_names(df)

    # iterating through unique columns
    unique_cols = preparator.get_unique_column_names(df)

    # Removing white spaces from values
    df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Replacing 'x' with True values - Table still contains different values, e.g. 1's
    df.replace('x', True, inplace=True)

    df_reshaped = pd.DataFrame()
    for col in unique_cols:
        if col in dupcols:
            df_temp = df.xs(col, axis=1, level=0, drop_level=False)
            l2_colname = df_temp.columns.get_level_values(1)
            df_reshaped[l2_colname] = df_temp
        else:
            df_reshaped[col] = df.loc[:, col]

    return df_reshaped


def main():

    # Get download folder from user
    download_dir = finder.get_download_folder()

    # Get input directory from user
    input_dir = userinput.get_user_input("Input directory", default=download_dir)

    # List files in the input directory
    file_list = finder.get_file_list(input_dir, extensions=[".xlsx", ".xls"])
    finder.print_enumerated_list(file_list)

    # Get selected file from user
    selected_file_num = userinput.get_user_input("Select a file by number", default="1")
    selected_file_path = file_list[int(selected_file_num) - 1]

    # Create dataframe from excel file
    df = pd.read_excel(selected_file_path, header=[0,1])

    # Preprocess the DataFrame: strip whitespace and handle missing values
    df.map(lambda x: x.strip() if isinstance(x, str) else x).fillna('null')

    # Reshaping dataframe
    df = get_reshaped_dataframe(df)

    # Retrieving dataframe column names, transform and re-assign to df
    colnames = df.columns
    db_ready_colnames = preparator.get_db_ready_column_names(colnames)
    df.columns = db_ready_colnames[:]

    # Reordering columns to have 'product_name_alias' first if it exists
    cols_to_reorder = ['product_name_alias', 'fat_content_minimum%', 'fat_content_maximum%', 'protein_content_minimum%', 'protein_content_maximum%']
    df = finder.reorder_dataframe_columns(df, cols_to_reorder)

    res = store_dataframe_to_db(df)
    print(res)


if __name__ == "__main__":
    main()






