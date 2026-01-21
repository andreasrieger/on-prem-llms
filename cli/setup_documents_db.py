import os
import pandas as pd
from mypackage import finder, userinput, splitter
from sqlalchemy import Table, Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase

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
        Column('chunk_number', Integer),
        Column('text', String),
    )

    Base.metadata.create_all(engine)

    return df.to_sql(documents_table.name, index=False, con=engine, if_exists='replace')


def main():
    download_dir = finder.get_download_folder()

    # Get input directory from user
    input_dir = userinput.get_user_input("Input directory", default=download_dir)

    # List PDF files in the input directory
    file_list = finder.get_file_list(input_dir, extensions=[".pdf"])
    finder.print_enumerated_list(file_list)

    # Get selected file from user
    selected_file_num = userinput.get_user_input("Select a file by number", default="1")
    selected_file_path = file_list[int(selected_file_num) - 1]
    selected_file_name = os.path.basename(selected_file_path)

    # Process document file
    file_content_list = finder.get_pdf_contents(selected_file_path)

    # Create a DataFrame from the content list with chunks
    chunked_data = []
    for i, content in enumerate(file_content_list):
        page_number = i + 1
        chunks = splitter.get_chunks_from_text(content)
        for chunk in chunks:
            # chunk_number = len(chunked_data)
            chunked_data.append((page_number, chunks.index(chunk), chunk, selected_file_name))

    df = pd.DataFrame(chunked_data, columns=["page_number", "chunk_number", "text", "source"])

    # Store DataFrame in database
    res = store_chunks_in_db(df)
    print(f"Stored {res} chunks in database.")

    




if __name__ == "__main__":
    main()
