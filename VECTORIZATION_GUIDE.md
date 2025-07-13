# Jozef Neo-Latin Studies Chatbot - Vectorization Guide

This guide explains how to prepare the document vectorization for the Jozef chatbot before deploying it to production.

## Overview

The vectorization process has been separated from the main chatbot application to improve production performance and deployment flexibility. The `vectorize.py` script handles all document processing and vector database creation.

## Prerequisites

1. **Ollama Server**: Make sure Ollama is running and accessible
   ```bash
   # Check if Ollama is running
   ollama list
   
   # If not running, start it
   ollama serve
   ```

2. **Embedding Model**: Ensure the embedding model is available
   ```bash
   # Pull the embedding model (if not already available)
   ollama pull nomic-embed-text
   ```

3. **PDF Documents**: Place your Neo-Latin handbooks and documents in the `my_pdfs/` directory

## Usage

### Basic Vectorization

To vectorize all PDF documents in the default directory:

```bash
python vectorize.py
```

### Advanced Options

```bash
# Specify a different PDF directory
python vectorize.py --pdf-dir /path/to/your/pdfs

# Force reindexing (rebuild the entire vector database)
python vectorize.py --force-reindex

# Only verify existing vectorization
python vectorize.py --verify-only
```

### Full Example

```bash
# 1. Place PDF files in the my_pdfs directory
cp your_handbooks/*.pdf my_pdfs/

# 2. Run vectorization
python vectorize.py

# 3. Verify the vectorization worked
python vectorize.py --verify-only

# 4. Start the chatbot
python app.py
```

## What the Vectorization Script Does

1. **Checks Prerequisites**: Verifies Ollama connection, PDF files, and embedding model availability
2. **Loads PDFs**: Extracts text from all PDF files in the specified directory
3. **Chunks Documents**: Splits documents into smaller, searchable chunks
4. **Creates Embeddings**: Generates vector embeddings for each chunk using the embedding model
5. **Stores Vectors**: Saves embeddings to a ChromaDB vector database
6. **Verifies Results**: Runs test queries to ensure vectorization was successful

## Output

The script creates:
- `chroma_db/`: Directory containing the vector database
- Detailed progress logs showing which documents were processed
- Verification results with test queries

## Configuration

You can customize the vectorization process by modifying `config.py`:

```python
# Document Processing Settings
PDF_DIRECTORY = "./my_pdfs"           # Directory containing PDF files
CHUNK_SIZE = 800                      # Size of text chunks
CHUNK_OVERLAP = 100                   # Overlap between chunks

# Vector Database Settings
CHROMA_PERSIST_DIRECTORY = "./chroma_db"  # Vector database directory
COLLECTION_NAME = "neolatin_documents"    # Collection name

# Embedding Model
EMBEDDING_MODEL = "nomic-embed-text"      # Ollama embedding model
```

## Production Deployment

For production deployment:

1. **Pre-vectorize on Development Machine**:
   ```bash
   python vectorize.py
   ```

2. **Copy Vector Database to Production**:
   ```bash
   # Copy the entire chroma_db directory to production server
   rsync -av chroma_db/ production_server:path/to/chatbot/chroma_db/
   ```

3. **Start Production Chatbot**:
   The chatbot will automatically load the existing vector database without reprocessing documents.

## Troubleshooting

### "No PDF files found"
- Ensure PDF files are in the correct directory (`my_pdfs/` by default)
- Check file permissions

### "Error connecting to Ollama"
- Verify Ollama is running: `ollama list`
- Check the Ollama base URL in `config.py`
- Ensure the embedding model is available: `ollama pull nomic-embed-text`

### "Vector store not initialized"
- Run `python vectorize.py` to create the vector database
- Check that the `chroma_db` directory was created and contains data

### "Verification tests failed"
- Try rerunning with `--force-reindex` to rebuild the entire database
- Check that your PDF files contain searchable text (not just images)

## File Structure After Vectorization

```
ragbot/
├── app.py                 # Main Flask application
├── vectorize.py          # Vectorization script
├── config.py             # Configuration settings
├── my_pdfs/              # PDF documents
│   ├── handbook1.pdf
│   └── handbook2.pdf
├── chroma_db/            # Vector database (created by vectorize.py)
│   ├── chroma.sqlite3
│   └── ...
└── src/
    ├── rag_engine.py     # RAG engine (loads existing vectors)
    └── document_processor.py
```

## Performance Notes

- **First Run**: May take several minutes depending on document size and quantity
- **Subsequent Runs**: Only new documents are processed (unless `--force-reindex` is used)
- **Production**: No document processing occurs, only vector database loading

## Integration with Chatbot

The chatbot (`app.py`) will automatically:
1. Load the existing vector database on startup
2. Display the number of available document chunks
3. Warn if no vector database is found
4. Provide instructions to run vectorization if needed

This separation ensures fast startup times and predictable performance in production environments.
