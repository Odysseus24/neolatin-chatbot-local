"""
Document processing module for the Jozef Neo-Latin Studies Chatbot.
Handles PDF ingestion, text extraction, chunking, and vector storage.
"""

import os
import glob
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DocumentProcessor:
    """Handles document processing and vector storage operations."""
    
    def __init__(self, auto_initialize: bool = True):
        """
        Initialize the document processor with embeddings and vector store.
        
        Args:
            auto_initialize: If True, attempt to initialize vector store on startup.
                           If False, vector store will be initialized on demand.
        """
        self.embeddings = OllamaEmbeddings(
            base_url=config.OLLAMA_BASE_URL,
            model=config.EMBEDDING_MODEL
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.vector_store = None
        if auto_initialize:
            self._initialize_vector_store()
    
    def _initialize_vector_store(self, create_if_missing: bool = False):
        """
        Initialize or load existing Chroma vector store.
        
        Args:
            create_if_missing: If True, create a new vector store if none exists.
                             If False, only load existing vector stores.
        """
        try:
            # Check if persist directory exists
            if not os.path.exists(config.CHROMA_PERSIST_DIRECTORY):
                if create_if_missing:
                    os.makedirs(config.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
                    print(f"Created vector store directory: {config.CHROMA_PERSIST_DIRECTORY}")
                else:
                    print(f"Vector store directory does not exist: {config.CHROMA_PERSIST_DIRECTORY}")
                    print("Run 'python vectorize.py' to create and populate the vector store.")
                    return False
            
            # Initialize vector store (this will load existing data if present)
            self.vector_store = Chroma(
                collection_name=config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=config.CHROMA_PERSIST_DIRECTORY
            )
            
            # Test if vector store was properly initialized by trying to get collection count
            try:
                doc_count = len(self.vector_store.get()['ids']) if self.vector_store.get()['ids'] else 0
                if doc_count > 0:
                    print(f"Vector store loaded successfully with {doc_count} documents")
                else:
                    print("Vector store loaded but is empty")
                    if not create_if_missing:
                        print("Run 'python vectorize.py' to populate the vector store.")
                return True
            except Exception as e:
                print(f"Vector store created but cannot access collection: {e}")
                if not create_if_missing:
                    print("This might indicate the vector store needs to be recreated.")
                    print("Run 'python vectorize.py --force-reindex' to rebuild it.")
                raise e
                
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            if create_if_missing:
                print("This might be normal for first-time setup. Continuing...")
            else:
                print("Vector store not available. Run 'python vectorize.py' to create it.")
            # Set vector_store to None on failure
            self.vector_store = None
            return False
    
    def load_pdf_documents(self, pdf_directory: Optional[str] = None) -> List[Document]:
        """Load and extract text from PDF files."""
        if pdf_directory is None:
            pdf_directory = config.PDF_DIRECTORY
        
        documents = []
        pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {pdf_directory}")
            return documents
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                print(f"Processing: {os.path.basename(pdf_file)}")
                loader = PyPDFLoader(pdf_file)
                pdf_documents = loader.load()
                
                # Add metadata
                for doc in pdf_documents:
                    doc.metadata.update({
                        'source_file': os.path.basename(pdf_file),
                        'file_path': pdf_file,
                        'document_type': 'neolatin_handbook'
                    })
                
                documents.extend(pdf_documents)
                print(f"Loaded {len(pdf_documents)} pages from {os.path.basename(pdf_file)}")
                
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
        
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for better retrieval."""
        if not documents:
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def add_documents_to_vector_store(self, documents: List[Document]) -> bool:
        """Add documents to the vector store."""
        if not documents:
            print("No documents to add")
            return False
        
        if not self.vector_store:
            print("Vector store not initialized - attempting to initialize with creation enabled...")
            self._initialize_vector_store(create_if_missing=True)
            if not self.vector_store:
                print("Failed to initialize vector store - creating new one for this session...")
                try:
                    # Ensure directory exists
                    os.makedirs(config.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
                    self.vector_store = Chroma(
                        collection_name=config.COLLECTION_NAME,
                        embedding_function=self.embeddings,
                        persist_directory=config.CHROMA_PERSIST_DIRECTORY
                    )
                except Exception as e:
                    print(f"Cannot create vector store: {e}")
                    return False
        
        try:
            # Check if documents already exist to avoid duplicates
            existing_sources = set()
            try:
                existing_data = self.vector_store.get()
                if existing_data and 'metadatas' in existing_data and existing_data['metadatas']:
                    existing_sources = {
                        metadata.get('source_file', '') 
                        for metadata in existing_data['metadatas']
                        if metadata and isinstance(metadata, dict) and 'source_file' in metadata
                    }
            except Exception as e:
                print(f"Warning: Could not check existing documents: {e}")
                # Continue anyway, duplicates are manageable
            
            # Filter out documents that already exist
            new_documents = [
                doc for doc in documents 
                if doc.metadata.get('source_file', '') not in existing_sources
            ]
            
            if not new_documents:
                print("All documents already exist in vector store")
                return True
            
            print(f"Adding {len(new_documents)} new documents to vector store...")
            
            # Add documents to vector store
            self.vector_store.add_documents(new_documents)
            
            print(f"Successfully added {len(new_documents)} documents to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False
    
    def process_all_pdfs(self) -> bool:
        """Complete pipeline: load PDFs, chunk, and add to vector store."""
        print("Starting document processing pipeline...")
        
        # Load documents
        documents = self.load_pdf_documents()
        if not documents:
            print("No documents to process")
            return False
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        if not chunks:
            print("No chunks created")
            return False
        
        # Add to vector store
        success = self.add_documents_to_vector_store(chunks)
        
        if success:
            print("Document processing pipeline completed successfully")
            if self.vector_store:
                try:
                    doc_count = len(self.vector_store.get()['ids']) if self.vector_store.get()['ids'] else 0
                    print(f"Total documents in vector store: {doc_count}")
                except Exception as e:
                    print(f"Could not get document count: {e}")
        
        return success
    
    def get_vector_store(self) -> Optional[Chroma]:
        """Get the vector store instance."""
        return self.vector_store
    
    def search_documents(self, query: str, k: int = 4) -> List[Document]:
        """Search for relevant documents."""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

def main():
    """Main function for testing document processing."""
    # Enable auto-initialization for testing
    processor = DocumentProcessor(auto_initialize=True)
    success = processor.process_all_pdfs()
    
    if success:
        # Test search
        test_query = "Neo-Latin literature"
        results = processor.search_documents(test_query)
        print(f"\nTest search for '{test_query}' returned {len(results)} results")
        for i, doc in enumerate(results):
            print(f"Result {i+1}: {doc.metadata.get('source_file', 'Unknown')} - {doc.page_content[:100]}...")

if __name__ == "__main__":
    main()
