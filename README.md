# RAG with Anthropic's Citation
- Document Q&A system integrating Anthropic's citation and Microsoft's Markitdown to provide transparent, source-backed responses. The system processes documents and generates answers with precise in-text citations, preserving the traceability of information across multiple document. Uses markitdown for multiple file type management.This project uses uv for python management.
- Details here :
  * Markitdown : https://github.com/microsoft/markitdown
  * UV : https://github.com/astral-sh/uv
  * Anthropic Citation : https://www.anthropic.com/news/introducing-citations-api
## Features
- Multi-document processing (PDF, TXT, DOCX, PPTX)
- In-text citations with source tracking
- Interactive chat interface
- Citation toggle

## Setup

### Clone the repository

- git clone https://github.com/Croups/rag-citation.git
- cd rag-citation

### Install dependencies

- uv venv
- uv pip sync

### Create a .env file
 - ANTHROPIC_API_KEY=your-api-key

## How to run

- uv run streamlit run app.py

  
## Structure
- rag-citation/
- ├── app.py          # Streamlit interface
- ├── rag.py          # RAG implementation
- ├── pyproject.toml  # Project configuration
- └── .env           # Environment variables

## License
MIT
