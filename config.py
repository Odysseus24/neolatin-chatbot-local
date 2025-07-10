"""
Configuration settings for the Jozef Neo-Latin Studies Chatbot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Ollama Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Vector Database Settings
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "neolatin_documents")

# Document Processing Settings
PDF_DIRECTORY = os.getenv("PDF_DIRECTORY", "./my_pdfs")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Embedding Model Settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# Flask App Settings
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Chat Settings
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "5"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# System Prompt for the Chatbot
SYSTEM_PROMPT = """You are Jozef, a knowledgeable assistant specializing in Neo-Latin Studies. 
You have access to handbooks and scholarly materials about Neo-Latin literature, history, and culture.

Guidelines:
- Provide accurate, scholarly information about Neo-Latin topics
- Draw from your knowledge of the handbooks when relevant
- Answer naturally without explicitly mentioning your sources unless asked
- If you're unsure about something, acknowledge the uncertainty
- Be helpful and educational in your responses
- Maintain an academic but approachable tone
"""
