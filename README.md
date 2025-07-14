# Jozef - Neo-Latin Studies Chatbot

A sophisticated RAG (Retrieval-Augmented Generation) chatbot specialized in Neo-Latin Studies, powered by Ollama, Langchain, Chroma vector database, and featuring a responsive Bootstrap interface with real-time streaming responses.

## ✨ Features

- **🤖 Intelligent Document Processing**: Automatically processes OCRed PDFs of Neo-Latin handbooks
- **🔍 Advanced RAG System**: Combines document retrieval with conversational AI using Chroma vector database
- **💾 Memory Management**: Maintains conversation context for natural dialogue
- **🎨 Clean Web Interface**: Professional, scholarly interface with responsive design
- **🔒 Privacy-First**: Uses local Ollama LLM server - no data sent to external APIs
- **⚡ Real-time Streaming**: Smooth, progressive response streaming with optimized token limits
- **🎯 Smart Context Usage**: Clearly indicates when responding from handbooks vs. general knowledge
- **📝 Clean Chat Experience**: Text-only interface optimized for academic research

## 🛠️ Prerequisites

1. **Ollama Server**: Make sure Ollama is installed and running
   ```bash
   # Install Ollama (macOS)
   brew install ollama
   
   # Start Ollama service
   ollama serve
   
   # Pull the required model
   ollama pull llama3.1
   ```

2. **Python Environment**: Python 3.8+ with virtual environment support

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd ragbot
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize settings:

```env
# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1  # Change to your preferred model

# Flask Settings  
FLASK_HOST=127.0.0.1
FLASK_PORT=5001

# Document Settings
PDF_DIRECTORY=./my_pdfs
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Chat Settings
MAX_CONVERSATION_HISTORY=5
TEMPERATURE=0.3
MAX_TOKENS=1024  # Optimized for complete responses
```

## 🎯 Usage

### 1. Add PDF Documents

Place your Neo-Latin handbooks (OCRed PDFs) in the `my_pdfs` directory:
```bash
cp your_neolatin_handbook.pdf my_pdfs/
```

**📄 Copyright Protection**: PDF files in `my_pdfs/` are automatically excluded from Git commits to respect copyright. The directory structure is preserved with a `.gitkeep` file. The existing sample documents remain tracked as reference documents, but any new PDF files you add will be automatically ignored.

### 2. Vectorize Documents (Required Before First Use)

**Important**: Before starting the chatbot, you must vectorize your documents:

```bash
# Process all PDF documents and create vector database
python vectorize.py

# Optional: Force rebuild of vector database
python vectorize.py --force-reindex

# Optional: Verify vectorization worked
python vectorize.py --verify-only
```

See the [Vectorization Guide](VECTORIZATION_GUIDE.md) for detailed instructions.

**🔄 Adding New Documents**: To add new PDF documents to an existing setup:
1. Copy new PDFs to `my_pdfs/` directory
2. Run `python vectorize.py` (only processes new documents)
3. **Restart the chatbot** (`Ctrl+C` then `python app.py`) to load updated database

### 3. Start the Application

```bash
# Start the web application
python app.py
```

Then open your browser to: `http://localhost:5001`

### 4. Using the Chat Interface

- **💬 Text Chat**: Type your questions about Neo-Latin studies in the input field
  - Supports real-time streaming responses with typing indicators
  - Clear indication when responses use handbooks ("According to my handbooks...")
  - Transparent fallback to general knowledge when handbooks don't contain relevant info
  - Conversation memory for context-aware discussions
  - Clean, academic-focused interface

### 4. Process Documents

Documents are processed using the separate vectorization script:
```bash
# Process documents before starting the chatbot
python vectorize.py
```

### 5. Command Line Testing

```bash
# Test the RAG engine directly
python src/rag_engine.py
```

## 📁 Project Structure

```
ragbot/
├── app.py                      # Flask web application
├── config.py                   # Configuration settings  
├── requirements.txt            # Python dependencies
├── vectorize.py               # Document vectorization script
├── VECTORIZATION_GUIDE.md     # Detailed vectorization guide
├── .env.example               # Environment variables template
├── .env                       # Environment variables (local)
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── my_pdfs/                   # PDF documents directory
│   ├── .gitkeep              # Preserves directory in Git
│   ├── Knight_Tilg 2018.pdf  # Sample document (tracked in Git for demo purposes)
│   └── Moul 2017.pdf         # Additional sample document
├── src/
│   ├── document_processor.py  # PDF processing and vectorization core
│   └── rag_engine.py         # RAG logic and conversation management
├── templates/
│   ├── index.html            # Main web interface
│   └── index_clean.html      # Alternative clean interface (unused)
├── static/                    # Static web assets
│   ├── css/
│   └── js/
└── chroma_db/                # Vector database (created by vectorize.py)
```

## 🔧 Key Components

### Document Processor (`src/document_processor.py`)
- Loads and chunks PDF documents
- Creates embeddings using Ollama embedding models
- Stores vectors in Chroma database
- Handles duplicate detection and incremental updates

### RAG Engine (`src/rag_engine.py`)
- Manages conversation memory
- Retrieves relevant document chunks
- Integrates with Ollama for response generation
- Provides streaming response capabilities
- Formats context for optimal results

### Vectorization Script (`vectorize.py`)
- Standalone script for document processing
- Pre-production vectorization pipeline
- Comprehensive error checking and verification
- Command-line interface with multiple options

### Web Interface (`templates/index.html`)
- Clean, responsive design with Bootstrap
- Real-time streaming chat interface with typing indicators
- Academic-focused user experience
- Smart response attribution system
- Responsive design for mobile and desktop

## ⚙️ Advanced Configuration

### Custom Models
Change the Ollama model in `.env`:
```env
OLLAMA_MODEL=mistral  # or codellama, neural-chat, etc.
```

### Streaming Settings
Adjust response streaming behavior:
```env
MAX_TOKENS=2048      # Larger token limit for longer responses
TEMPERATURE=0.5      # Higher creativity vs consistency
```

### Embedding Models
Modify the embedding model in `.env`:
```env
EMBEDDING_MODEL=nomic-embed-text  # Default Ollama embedding model
```

### Chunk Settings
Adjust document chunking in `.env`:
```env
CHUNK_SIZE=1200      # Larger chunks for more context
CHUNK_OVERLAP=200    # More overlap for better continuity
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is available: `ollama list`
   - Pull the model if needed: `ollama pull llama3.1`
   - Verify the URL in `.env`

2. **No Documents Found**:
   - Check PDF files are in `my_pdfs/` directory
   - Ensure files have `.pdf` extension
   - Run `python vectorize.py` to process documents
   - Check vectorization guide: `VECTORIZATION_GUIDE.md`

3. **Vector Database Issues**:
   - Run `python vectorize.py --verify-only` to test existing database
   - Use `python vectorize.py --force-reindex` to rebuild completely
   - Check that `chroma_db/` directory exists and contains data

4. **Streaming Issues**:
   - Check browser console for JavaScript errors
   - Try refreshing the page
   - Verify `/chat/stream` endpoint is responding
   - Check Flask debug output for server errors

5. **Incomplete Responses**:
   - Increase `MAX_TOKENS` in `.env` (current: 1024)
   - Reduce `CHUNK_SIZE` to leave more room for responses
   - Check Ollama model performance with `ollama show llama3.1`

6. **Memory Issues**:
   - Reduce `CHUNK_SIZE` in `.env`
   - Limit `MAX_CONVERSATION_HISTORY`
   - Restart the application periodically

7. **New Documents Not Available**:
   - After adding PDFs and running `python vectorize.py`, restart the chatbot
   - Check that vectorization completed successfully with no errors
   - Verify new document count with `python vectorize.py --verify-only`

### Debug Mode

Enable debug mode in `.env`:
```env
FLASK_DEBUG=True
```

View detailed logs in the terminal where you run `python app.py`.

## 📄 Copyright & File Management

### PDF Document Handling
- **Local Storage**: Add your PDF documents to the `my_pdfs/` directory for processing
- **Git Protection**: All **new** PDF files in `my_pdfs/` are automatically excluded from Git commits
- **Sample Document**: The existing sample documents remain tracked as reference/demo documents
- **Directory Preservation**: The `my_pdfs/` folder structure is maintained via `.gitkeep`
- **Privacy First**: Your research documents remain local and are never pushed to remote repositories

### Sharing Your Setup
When sharing this project or deploying to production:
```bash
# The repository contains the code structure but no PDF content
git clone <your-repo-url>
cd ragbot

# Add your own PDF documents locally
cp your_documents/*.pdf my_pdfs/

# Vectorize your documents
python vectorize.py
```

## 🎓 Academic Use

This chatbot is designed for scholarly research in Neo-Latin Studies. It:
- Clearly distinguishes between handbook-based and general knowledge responses
- Maintains academic tone and accuracy
- Supports complex historical and literary queries
- Preserves conversation context for extended research sessions
- Protects privacy with local processing
- Provides transparent source attribution through response prefixes

## � Production Deployment

### Pre-production Vectorization

For production deployment, vectorize documents beforehand to improve startup performance:

```bash
# On your development machine:
# 1. Add all production PDF documents to my_pdfs/
cp production_handbooks/*.pdf my_pdfs/

# 2. Vectorize all documents
python vectorize.py

# 3. Verify vectorization
python vectorize.py --verify-only

# 4. The chroma_db/ directory now contains the production-ready vector database
```

### Production Server Setup

```bash
# 1. Copy project to production server (excluding .env and chroma_db)
rsync -av --exclude='.env' --exclude='chroma_db' ragbot/ production_server:chatbot/

# 2. Copy the vectorized database
rsync -av chroma_db/ production_server:chatbot/chroma_db/

# 3. On production server:
cd chatbot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure production environment
cp .env.example .env
# Edit .env with production settings

# 5. Start the application
python app.py
```

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
# Vector database should be pre-built and included in the image

EXPOSE 5001
CMD ["python", "app.py"]
```

## �🔄 Development Workflow

### Working Locally
```bash
# Pull latest changes
git pull origin main

# Make your changes...

# Test locally
python app.py

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

### Adding New Features
1. Create a new branch: `git checkout -b feature-name`
2. Make your changes
3. Test thoroughly
4. Commit and push: `git push origin feature-name`
5. Create a pull request on GitHub

### Environment Management
- Never commit `.env` files (use `.env.example`)
- Update `requirements.txt` when adding dependencies: `pip freeze > requirements.txt`
- Keep `chroma_db/` local (it's in `.gitignore`)

## 🤝 Contributing

To add new features or improve existing functionality:

1. **Document processing enhancements**: `src/document_processor.py`
2. **RAG improvements**: `src/rag_engine.py`  
3. **Streaming optimizations**: Response streaming logic in `app.py`
4. **UI/UX updates**: `templates/index.html`
5. **Configuration options**: `config.py`

## 📄 License

This project is intended for academic and research purposes in Neo-Latin Studies.

---

## 🚀 Quick Start Checklist

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Install and start Ollama: `ollama serve`
- [ ] Pull models: `ollama pull llama3.1` and `ollama pull nomic-embed-text`
- [ ] Add PDFs to `my_pdfs/`
- [ ] **Vectorize documents: `python vectorize.py`**
- [ ] Run: `python app.py`
- [ ] Open `http://localhost:5001`
- [ ] **When adding new PDFs**: Re-run `python vectorize.py` and restart the app
