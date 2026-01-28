# On-Prem LLMs

Utilities for running LLMs on-premises with RAG (Retrieval-Augmented Generation) and SQL agent capabilities.

## Overview

This project provides tools for building AI agents that run entirely on-premises using Ollama, Qdrant vector store, and LangChain. It includes two main agent types:

- **RAG Agent**: Query documents using vector similarity search and LLM-powered question answering
- **SQL Agent**: Interact with SQL databases through natural language queries

## Features

- 🔒 Fully on-premises deployment with local LLM models (via Ollama)
- 📚 Document processing and vector storage with Qdrant
- 🤖 LangChain-based agent orchestration
- 💾 SQLite database integration
- 📄 PDF document processing
- 🔍 Semantic search capabilities

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd on-prem-llms
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running locally
- Required Ollama models:
  - `nomic-embed-text` (for embeddings)
  - `ministral-3` (for chat/completion)

Pull the models with:
```bash
ollama pull nomic-embed-text
ollama pull ministral-3
```

## Usage

### RAG Agent

Query documents using semantic search and LLM-powered answers:

```bash
python rag_agent.py
```

The RAG agent:
- Loads document chunks from a SQLite database
- Creates vector embeddings using Ollama
- Stores vectors in Qdrant (in-memory)
- Retrieves relevant context for user queries
- Generates answers with source citations

### SQL Agent

Query SQL databases using natural language:

```bash
python sql_agent.py
```

The SQL agent:
- Connects to a SQLite database
- Translates natural language to SQL queries
- Executes queries safely (read-only)
- Returns results in natural language

## Project Structure

```
on-prem-llms/
├── src/mypackage/          # Core package modules
│   ├── dbmanager.py        # Database management utilities
│   ├── embedder.py         # Embedding generation
│   ├── finder.py           # File and path utilities
│   ├── generator.py        # Text generation utilities
│   ├── knowledger.py       # Knowledge base management
│   ├── preparator.py       # Data preparation
│   ├── retriever.py        # Document retrieval
│   ├── splitter.py         # Text chunking
│   └── userinput.py        # User input handling
├── rag_agent.py            # RAG agent implementation
├── sql_agent.py            # SQL agent implementation
├── data/                   # Data storage directory
├── notebooks/              # Jupyter notebooks
├── pyproject.toml          # Package configuration
└── requirements.txt        # Python dependencies
```

## Dependencies

Core dependencies include:
- `langchain` - LLM application framework
- `langchain-ollama` - Ollama integration
- `langchain-qdrant` - Qdrant vector store integration
- `qdrant-client` - Qdrant database client
- `pandas` - Data manipulation
- `SQLAlchemy` - SQL toolkit
- `pypdf` - PDF processing

## Configuration

The project uses:
- **Embedding model**: `nomic-embed-text` (768-dimensional vectors)
- **Chat model**: `ministral-3` (temperature: 0.0)
- **Vector store**: Qdrant (in-memory mode)
- **Distance metric**: Cosine similarity

## License

MIT License

## Author

Andreas Rieger (dev@rieger.digital)
