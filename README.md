# Jozef - Neo-Latin Studies Chatbot

A sophisticated RAG (Retrieval-Augmented Generation) chatbot specialized in Neo-Latin Studies, powered by Ollama, Langchain, Chroma vector database, and featuring a Renaissance-inspired Bootstrap interface with real-time streaming responses.

## ✨ Features

- **🤖 Intelligent Document Processing**: Automatically processes OCRed PDFs of Neo-Latin handbooks
- **🔍 Advanced RAG System**: Combines document retrieval with conversational AI using Chroma vector database
- **💾 Memory Management**: Maintains conversation context for natural dialogue
- **🎨 Renaissance-Inspired UI**: Clean, scholarly interface with period-appropriate design
- **📚 Source Attribution**: Shows which documents informed each response (when relevant)
- **🔒 Privacy-First**: Uses local Ollama LLM server - no data sent to external APIs
- **⚡ Real-time Streaming**: Smooth, progressive response streaming with optimized token limits
- **� Clean Chat Experience**: Text-only interface optimized for academic research

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

### 2. Start the Application

```bash
# Start the web application
python app.py
```

Then open your browser to: `http://localhost:5001`

### 3. Using the Chat Interface

- **💬 Text Chat**: Type your questions about Neo-Latin studies in the input field
  - Supports real-time streaming responses with typing indicators
  - Automatic source attribution when relevant
  - Conversation memory for context-aware discussions
  - Clean, academic-focused interface

### 4. Process Documents

Use the "Process Documents" button in the web interface, or run manually:
```bash
python src/document_processor.py
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
├── .env.example               # Environment variables template
├── .env                       # Environment variables (local)
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── my_pdfs/                   # PDF documents directory
│   └── test.pdf              # Sample document
├── src/
│   ├── document_processor.py  # PDF processing and vectorization
│   └── rag_engine.py         # RAG logic and conversation management
├── templates/
│   ├── index.html            # Main Renaissance-inspired web interface
│   └── test_streaming.html   # Streaming test interface
├── static/                    # Static web assets
│   ├── css/
│   └── js/
├── chroma_db/                # Vector database (auto-created)
└── tts_cache/                # Cached files (legacy, can be removed)
```

## 🔧 Key Components

### Document Processor (`src/document_processor.py`)
- Loads and chunks PDF documents
- Creates embeddings using HuggingFace models
- Stores vectors in Chroma database
- Handles duplicate detection

### RAG Engine (`src/rag_engine.py`)
- Manages conversation memory
- Retrieves relevant document chunks
- Integrates with Ollama for response generation
- Provides streaming response capabilities
- Formats context for optimal results

### Web Interface (`templates/index.html`)
- Renaissance-inspired design with Bootstrap
- Real-time streaming chat interface with typing indicators
- Clean, academic-focused user experience
- Source attribution display
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
Modify the embedding model in `config.py`:
```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Higher quality
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
   - Run document processor manually to see errors

3. **Streaming Issues**:
   - Check browser console for JavaScript errors
   - Try refreshing the page
   - Verify `/chat/stream` endpoint is responding
   - Check Flask debug output for server errors

4. **Incomplete Responses**:
   - Increase `MAX_TOKENS` in `.env` (current: 1024)
   - Reduce `CHUNK_SIZE` to leave more room for responses
   - Check Ollama model performance with `ollama show llama3.1`

5. **Memory Issues**:
   - Reduce `CHUNK_SIZE` in `.env`
   - Limit `MAX_CONVERSATION_HISTORY`
   - Restart the application periodically

### Debug Mode

Enable debug mode in `.env`:
```env
FLASK_DEBUG=True
```

View detailed logs in the terminal where you run `python app.py`.

## 🎓 Academic Use

This chatbot is designed for scholarly research in Neo-Latin Studies. It:
- Provides citations and source references when relevant
- Maintains academic tone and accuracy
- Supports complex historical and literary queries
- Preserves conversation context for extended research sessions
- Protects privacy with local processing

## 🔄 Development Workflow

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
- [ ] Pull model: `ollama pull llama3.1`
- [ ] Add PDFs to `my_pdfs/`
- [ ] Run: `python app.py`
- [ ] Open `http://localhost:5001`
