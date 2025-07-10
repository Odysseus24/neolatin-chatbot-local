"""
RAG (Retrieval-Augmented Generation) engine for the Jozef Neo-Latin Studies Chatbot.
Handles conversation memory, document retrieval, and response generation.
"""

from typing import List, Dict, Optional, Any
import ollama
from langchain.schema import Document
from langchain.memory import ConversationBufferWindowMemory
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.document_processor import DocumentProcessor

class ConversationMemory:
    """Manages conversation history for the chatbot."""
    
    def __init__(self, max_history: Optional[int] = None):
        """Initialize conversation memory."""
        if max_history is None:
            max_history = config.MAX_CONVERSATION_HISTORY
            
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the conversation history."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only the last max_history messages
        if len(self.conversations[session_id]) > self.max_history * 2:  # *2 for user + assistant pairs
            self.conversations[session_id] = self.conversations[session_id][-self.max_history * 2:]
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get the conversation history for a session."""
        return self.conversations.get(session_id, [])
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]

class RAGEngine:
    """Main RAG engine that combines document retrieval with language generation."""
    
    def __init__(self):
        """Initialize the RAG engine."""
        self.document_processor = DocumentProcessor()
        self.memory = ConversationMemory()
        self.ollama_client = ollama.Client(host=config.OLLAMA_BASE_URL)
        
        # Test Ollama connection
        self._test_ollama_connection()
    
    def _test_ollama_connection(self):
        """Test connection to Ollama server."""
        try:
            models_response = self.ollama_client.list()
            available_models = [model.model for model in models_response.models]
            print(f"Connected to Ollama. Available models: {available_models}")
            
            # Check if the model exists (with or without :latest suffix)
            model_found = False
            for model in available_models:
                if model == config.OLLAMA_MODEL or model == f"{config.OLLAMA_MODEL}:latest":
                    model_found = True
                    break
            
            if not model_found:
                print(f"Warning: Model '{config.OLLAMA_MODEL}' not found. Available models: {available_models}")
                # Try to find a suitable generation model (not embedding model)
                generation_models = [m for m in available_models if m and 'embed' not in m.lower()]
                if generation_models:
                    config.OLLAMA_MODEL = generation_models[0]
                    print(f"Using model: {config.OLLAMA_MODEL}")
                else:
                    print("Error: No suitable generation models available in Ollama")
                    
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running and accessible")
    
    def _filter_by_content_relevance(self, documents: List[Document], query: str) -> List[Document]:
        """Filter documents by content relevance as a fallback method."""
        if not documents:
            return []
        
        # Simple keyword-based relevance check
        query_words = set(query.lower().split())
        relevant_docs = []
        
        for doc in documents:
            content_words = set(doc.page_content.lower().split())
            # Check if there's meaningful overlap between query and content
            overlap = len(query_words.intersection(content_words))
            if overlap >= 1:  # At least one word must match
                relevant_docs.append(doc)
        
        return relevant_docs
    
    def _should_show_sources(self, documents: List[Document], query: str, response: str) -> bool:
        """Determine if sources should be shown based on content relevance."""
        if not documents:
            return False
        
        # Check if the response likely used the document content
        query_lower = query.lower()
        response_lower = response.lower()
        
        # First check: Is this a Neo-Latin related query?
        neo_latin_keywords = ['neo-latin', 'neolatin', 'latin', 'renaissance', 'literature', 
                             'petrarch', 'humanist', 'classical', 'manuscript', 'poetry', 
                             'prose', 'scholarly', 'studies', 'fifteenth', 'sixteenth', 
                             'seventeenth', 'eighteenth', 'century', 'medieval', 'humanistic']
        
        query_has_academic_keywords = any(keyword in query_lower for keyword in neo_latin_keywords)
        
        # If the query is clearly not academic/Neo-Latin related, don't show sources
        general_keywords = ['weather', 'time', 'today', 'tomorrow', 'how are you', 
                           'hello', 'hi', 'thanks', 'thank you', 'goodbye', 'bye',
                           'current', 'news', 'politics', 'sports', 'food', 'cooking']
        
        if any(keyword in query_lower for keyword in general_keywords):
            return False
        
        # Second check: Does the response contain specific information that could come from documents?
        response_has_specific_info = any(keyword in response_lower for keyword in neo_latin_keywords)
        
        # Third check: Look for overlapping content between documents and response
        has_content_overlap = False
        for doc in documents:
            doc_content_lower = doc.page_content.lower()
            
            # Check for significant word overlap (5+ words in common)
            doc_words = set(doc_content_lower.split())
            response_words = set(response_lower.split())
            
            # Remove common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                           'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
                           'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                           'could', 'should', 'can', 'may', 'might', 'this', 'that',
                           'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
            
            doc_meaningful_words = doc_words - common_words
            response_meaningful_words = response_words - common_words
            
            overlap = len(doc_meaningful_words.intersection(response_meaningful_words))
            
            if overlap >= 3:  # At least 3 meaningful words in common
                has_content_overlap = True
                break
        
        # Show sources only if query is academic AND (response has specific info OR has content overlap)
        return query_has_academic_keywords and (response_has_specific_info or has_content_overlap)

    def retrieve_relevant_documents(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve relevant documents for the query."""
        return self.document_processor.search_documents(query, k=k)
    
    def format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents into context string."""
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source_file', 'Unknown source')
            content = doc.page_content.strip()
            
            # Limit context length
            if len(content) > 500:
                content = content[:500] + "..."
            
            context_parts.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def build_prompt(self, user_query: str, context: str, conversation_history: List[Dict[str, str]]) -> str:
        """Build the complete prompt for the language model."""
        
        # Start with system prompt
        prompt_parts = [config.SYSTEM_PROMPT]
        
        # Add context if available
        if context.strip():
            prompt_parts.append(f"\nRelevant information from Neo-Latin handbooks:\n{context}")
        
        # Add conversation history
        if conversation_history:
            prompt_parts.append("\nConversation history:")
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                role = "Human" if msg["role"] == "user" else "Assistant"
                prompt_parts.append(f"{role}: {msg['content']}")
        
        # Add current query
        prompt_parts.append(f"\nHuman: {user_query}")
        prompt_parts.append("\nAssistant: ")
        
        return "\n".join(prompt_parts)
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Ollama."""
        try:
            response = self.ollama_client.generate(
                model=config.OLLAMA_MODEL,
                prompt=prompt,
                options={
                    'temperature': config.TEMPERATURE,
                    'num_predict': config.MAX_TOKENS,
                    'stop': ['Human:', 'Assistant:']
                }
            )
            
            return response.get('response', '').strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def generate_response_stream(self, prompt: str):
        """Generate streaming response using Ollama for better perceived performance."""
        try:
            stream = self.ollama_client.generate(
                model=config.OLLAMA_MODEL,
                prompt=prompt,
                stream=True,
                options={
                    'temperature': config.TEMPERATURE,
                    'num_predict': config.MAX_TOKENS,
                    'stop': ['Human:', 'Assistant:']
                }
            )
            
            for chunk in stream:
                if 'response' in chunk:
                    yield chunk['response']
                if chunk.get('done', False):
                    break
                    
        except Exception as e:
            print(f"Error generating streaming response: {e}")
            yield "I apologize, but I'm having trouble generating a response right now. Please try again."

    def chat(self, user_query: str, session_id: str = "default") -> Dict[str, Any]:
        """Main chat function that handles the complete RAG pipeline."""
        
        # Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_documents(user_query)
        
        # Format context
        context = self.format_context(relevant_docs)
        
        # Get conversation history
        conversation_history = self.memory.get_conversation_history(session_id)
        
        # Build prompt
        prompt = self.build_prompt(user_query, context, conversation_history)
        
        # Generate response
        response = self.generate_response(prompt)
        
        # Add to conversation memory
        self.memory.add_message(session_id, "user", user_query)
        self.memory.add_message(session_id, "assistant", response)
        
        # Prepare deduplicated sources (one per file)
        sources_dict = {}
        for doc in relevant_docs:
            source_file = doc.metadata.get('source_file', 'Unknown')
            if source_file not in sources_dict:
                # Use the first occurrence (highest relevance) for each file
                sources_dict[source_file] = {
                    "file": source_file,
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
        
        # Determine if sources should be shown
        show_sources = self._should_show_sources(relevant_docs, user_query, response)
        
        # Prepare response data
        result = {
            "response": response,
            "sources": list(sources_dict.values()) if show_sources else [],
            "session_id": session_id
        }
        
        return result
    
    def clear_conversation(self, session_id: str = "default"):
        """Clear conversation history for a session."""
        self.memory.clear_conversation(session_id)
    
    def process_documents(self) -> bool:
        """Process all PDF documents in the configured directory."""
        return self.document_processor.process_all_pdfs()

def main():
    """Main function for testing the RAG engine."""
    rag = RAGEngine()
    
    # Process documents if needed
    print("Processing documents...")
    rag.process_documents()
    
    # Interactive chat
    print("\nJozef Neo-Latin Studies Chatbot")
    print("Type 'quit' to exit, 'clear' to clear conversation history")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'clear':
            rag.clear_conversation()
            print("Conversation history cleared.")
            continue
        elif not user_input:
            continue
        
        try:
            result = rag.chat(user_input)
            print(f"\nJozef: {result['response']}")
            
            if result['sources']:
                print(f"\n📚 Retrieved information from {len(result['sources'])} source(s)")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
