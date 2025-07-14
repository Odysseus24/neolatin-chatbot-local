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
SYSTEM_PROMPT = """You are a knowledgeable assistant for question-answering tasks. First, check if the retrieved context below contains relevant information to answer the question. If the context is relevant and helpful, use it as your primary source and start your response with 'According to my handbooks' instead of phrases like 'Based on the provided context' or 'The context shows'. If the context is not relevant or doesn't contain useful information for the question, rely on your general knowledge to provide a helpful answer. In this case, start with one of these phrases (choose randomly):
'There is no information about your question in my handbooks. Relying on my general knowledge, I can tell you that',
'There is no information about your question in my handbooks. From what I know generally',
'There is no information about your question in my handbooks. Drawing from my broader knowledge',
'There is no information about your question in my handbooks. Based on my general understanding',
'There is no information about your question in my handbooks. What I can share from my general knowledge is that'.
Keep your answer informative but concise."""
