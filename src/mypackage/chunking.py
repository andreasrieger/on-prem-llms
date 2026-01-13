from langchain_text_splitters import RecursiveCharacterTextSplitter


def text_chunking(text, chunk_size=1024):
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=64,
        add_start_index=True,
    )
    # Split the text into chunks
    chunks = text_splitter.split_text(text)
    return chunks