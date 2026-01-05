import langchain_text_splitters


def text_chunking(text, chunk_size=512):
    # Initialize the text splitter
    text_splitter = langchain_text_splitters.RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=0
    )
    # Split the text into chunks
    chunks = text_splitter.split_text(text)
    return chunks