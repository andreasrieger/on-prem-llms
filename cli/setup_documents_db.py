import os
import pandas as pd
from mypackage import finder, userinput, splitter
from sqlalchemy import Table, Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase



def get_text_chunks(file_content_list):
    return splitter.get_chunks_from_text(file_content_list)


def add_chunks_to_df(df):
    chunked_content = list(zip(df['page_number'], df['text'].apply(lambda x: splitter.get_chunks_from_text(x, chunk_size=512))))
    df_chunks = pd.DataFrame(chunked_content, columns=['page_number', 'chunks'])
    df_chunks = df_chunks.explode('chunks').reset_index(drop=True)
    df_chunks.loc[:, 'chunks'] = df_chunks.loc[:, 'chunks'].apply(lambda x: x.lower())
    # df_chunks['chunks_lower'] = df_chunks.loc[:, 'chunks'].apply(lambda x: x.lower())
    return df_chunks


def store_chunks_in_db(df):

    class Base(DeclarativeBase):
        pass


    data_dir = os.path.join(finder.get_git_root(), "data")
    db_name = 'documents.db'
    db_path = os.path.join(data_dir, db_name)

    engine = create_engine(f"sqlite:////{db_path}")

    documents_table = Table(
        'documents',
        Base.metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('page_number', Integer),
        Column('text', String),
    )

    Base.metadata.create_all(engine)

    return df.to_sql(documents_table.name, index=False, con=engine, if_exists='replace')


def main():
    download_dir = finder.get_download_folder()

    # Get input directory from user
    input_dir = userinput.get_user_input("Input directory", default=download_dir)

    # List files in the input directory
    file_list = finder.get_file_list(input_dir, extensions=[".pdf"])
    finder.print_enumerated_list(file_list)

    # Get selected file from user
    selected_file_num = userinput.get_user_input("Select a file by number", default="1")
    selected_file_path = file_list[int(selected_file_num) - 1]

    # Process document file
    file_content_list = finder.read_pdf_file(selected_file_path)

    for chunk in get_text_chunks(file_content_list):
        print(chunk)
    # df = pd.DataFrame(file_content_list, columns=['page_number', 'text'])


if __name__ == "__main__":
    main()
