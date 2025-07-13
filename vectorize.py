#!/usr/bin/env python3
"""
Vectorization script for the Jozef Neo-Latin Studies Chatbot.
This script handles the preprocessing and vectorization of PDF documents.
Run this script before deploying the chatbot to production.

Usage:
    python vectorize.py [--pdf-dir PATH] [--force-reindex]
"""

import argparse
import os
import sys
import time
from typing import List, Optional
import glob

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from src.document_processor import DocumentProcessor


class VectorizationManager:
    """Manages the complete vectorization pipeline for the chatbot."""
    
    def __init__(self, pdf_directory: Optional[str] = None, force_reindex: bool = False):
        """
        Initialize the vectorization manager.
        
        Args:
            pdf_directory: Directory containing PDF files to process
            force_reindex: Whether to force reindexing of existing documents
        """
        self.pdf_directory = pdf_directory or config.PDF_DIRECTORY
        self.force_reindex = force_reindex
        self.document_processor = DocumentProcessor()
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met for vectorization."""
        print("Checking prerequisites...")
        
        # Check if PDF directory exists
        if not os.path.exists(self.pdf_directory):
            print(f"❌ PDF directory does not exist: {self.pdf_directory}")
            return False
        
        # Check if there are PDF files
        pdf_files = glob.glob(os.path.join(self.pdf_directory, "*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in: {self.pdf_directory}")
            return False
        
        print(f"✅ Found {len(pdf_files)} PDF files in {self.pdf_directory}")
        
        # Check if Ollama is accessible
        try:
            from langchain_ollama import OllamaEmbeddings
            embeddings = OllamaEmbeddings(
                base_url=config.OLLAMA_BASE_URL,
                model=config.EMBEDDING_MODEL
            )
            # Try to create a test embedding
            test_embedding = embeddings.embed_query("test")
            if test_embedding:
                print(f"✅ Ollama embedding model '{config.EMBEDDING_MODEL}' is accessible")
            else:
                print(f"❌ Could not create test embedding with model '{config.EMBEDDING_MODEL}'")
                return False
        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
            print(f"Make sure Ollama is running and the model '{config.EMBEDDING_MODEL}' is available")
            return False
        
        # Check ChromaDB directory
        chroma_dir = config.CHROMA_PERSIST_DIRECTORY
        if os.path.exists(chroma_dir) and not self.force_reindex:
            existing_files = os.listdir(chroma_dir)
            if existing_files:
                print(f"⚠️  Existing vector database found at: {chroma_dir}")
                print("Use --force-reindex to rebuild the entire index")
        
        print("✅ All prerequisites met")
        return True
    
    def list_pdf_files(self) -> List[str]:
        """List all PDF files in the directory."""
        pdf_files = glob.glob(os.path.join(self.pdf_directory, "*.pdf"))
        return sorted(pdf_files)
    
    def get_existing_documents(self) -> set:
        """Get list of documents already in the vector store."""
        existing_sources = set()
        if self.document_processor.vector_store:
            try:
                existing_data = self.document_processor.vector_store.get()
                if existing_data and 'metadatas' in existing_data and existing_data['metadatas']:
                    existing_sources = {
                        metadata.get('source_file', '') 
                        for metadata in existing_data['metadatas']
                        if metadata and isinstance(metadata, dict) and 'source_file' in metadata
                    }
            except Exception as e:
                print(f"Warning: Could not check existing documents: {e}")
        return existing_sources
    
    def vectorize_documents(self) -> bool:
        """Run the complete vectorization pipeline."""
        start_time = time.time()
        print("=" * 60)
        print("STARTING VECTORIZATION PIPELINE")
        print("=" * 60)
        
        # List PDF files
        pdf_files = self.list_pdf_files()
        print(f"\nPDF files to process:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {os.path.basename(pdf_file)}")
        
        # Check existing documents if not forcing reindex
        if not self.force_reindex:
            existing_sources = self.get_existing_documents()
            if existing_sources:
                print(f"\nExisting documents in vector store: {len(existing_sources)}")
                for source in sorted(existing_sources):
                    print(f"  - {source}")
        
        # Clear vector store if force reindexing
        if self.force_reindex:
            print("\n🔄 Force reindexing enabled - clearing existing vector store...")
            chroma_dir = config.CHROMA_PERSIST_DIRECTORY
            if os.path.exists(chroma_dir):
                import shutil
                try:
                    shutil.rmtree(chroma_dir)
                    print(f"✅ Cleared existing vector store at {chroma_dir}")
                except Exception as e:
                    print(f"❌ Error clearing vector store: {e}")
                    return False
            
            # Reinitialize the document processor
            self.document_processor = DocumentProcessor()
        
        # Run the vectorization
        print(f"\n🚀 Starting document processing...")
        success = self.document_processor.process_all_pdfs()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        if success:
            print("✅ VECTORIZATION COMPLETED SUCCESSFULLY")
            print(f"⏱️  Total time: {duration:.2f} seconds")
            
            # Get final statistics
            if self.document_processor.vector_store:
                try:
                    doc_count = len(self.document_processor.vector_store.get()['ids'])
                    print(f"📊 Total document chunks in vector store: {doc_count}")
                except Exception as e:
                    print(f"Could not get final document count: {e}")
        else:
            print("❌ VECTORIZATION FAILED")
            print(f"⏱️  Time elapsed: {duration:.2f} seconds")
        
        print("=" * 60)
        return success
    
    def verify_vectorization(self) -> bool:
        """Verify that vectorization was successful by running test queries."""
        print("\n🔍 Verifying vectorization...")
        
        if not self.document_processor.vector_store:
            print("❌ No vector store available for verification")
            return False
        
        test_queries = [
            "Neo-Latin literature",
            "Renaissance",
            "humanist",
            "Latin poetry"
        ]
        
        all_tests_passed = True
        
        for query in test_queries:
            try:
                results = self.document_processor.search_documents(query, k=2)
                if results:
                    print(f"✅ Query '{query}': {len(results)} results found")
                    # Show a preview of the first result
                    if results[0].metadata.get('source_file'):
                        preview = results[0].page_content[:100].replace('\n', ' ')
                        print(f"   Preview: {preview}...")
                else:
                    print(f"⚠️  Query '{query}': No results found")
                    all_tests_passed = False
            except Exception as e:
                print(f"❌ Query '{query}': Error - {e}")
                all_tests_passed = False
        
        if all_tests_passed:
            print("✅ Vectorization verification completed successfully")
        else:
            print("⚠️  Some verification tests failed - vectorization may be incomplete")
        
        return all_tests_passed


def main():
    """Main function to run the vectorization script."""
    parser = argparse.ArgumentParser(
        description="Vectorize PDF documents for the Jozef Neo-Latin Studies Chatbot"
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        help=f"Directory containing PDF files (default: {config.PDF_DIRECTORY})"
    )
    parser.add_argument(
        "--force-reindex",
        action="store_true",
        help="Force reindexing of all documents, even if they already exist"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only run verification tests on existing vector store"
    )
    
    args = parser.parse_args()
    
    # Create vectorization manager
    vectorizer = VectorizationManager(
        pdf_directory=args.pdf_dir,
        force_reindex=args.force_reindex
    )
    
    if args.verify_only:
        print("Running verification tests only...")
        success = vectorizer.verify_vectorization()
        sys.exit(0 if success else 1)
    
    # Check prerequisites
    if not vectorizer.check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Run vectorization
    success = vectorizer.vectorize_documents()
    
    if success:
        # Run verification
        vectorizer.verify_vectorization()
        print("\n🎉 Vectorization pipeline completed successfully!")
        print("The chatbot is now ready for production deployment.")
    else:
        print("\n❌ Vectorization failed. Please check the logs above for errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
