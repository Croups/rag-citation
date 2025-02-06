# RAG with Claude's Citation
- Document Q&A system using Claude's citation features and Microsoft's Markitdown.

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
