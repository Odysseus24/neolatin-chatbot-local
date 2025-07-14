"""
Flask web application for the Jozef Neo-Latin Studies Chatbot.
Features a Renaissance-inspired Bootstrap interface.
"""

from flask import Flask, render_template, request, jsonify, session, Response
import uuid
import config
from src.rag_engine import RAGEngine
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize RAG engine
rag_engine = None

def initialize_rag_engine():
    """Initialize the RAG engine."""
    global rag_engine
    if rag_engine is None:
        try:
            print("Initializing RAG engine...")
            rag_engine = RAGEngine()
            print("RAG engine initialized.")
        except Exception as e:
            print(f"Error initializing RAG engine: {e}")
            rag_engine = None

@app.route('/')
def index():
    """Main chat interface."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        # Initialize RAG engine if not already done
        initialize_rag_engine()
        
        # Check if RAG engine is properly initialized
        if rag_engine is None:
            return jsonify({'error': 'RAG engine not available'}), 500
        
        data = request.json
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create session ID
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        # Get response from RAG engine
        result = rag_engine.chat(user_message, session_id)
        
        return jsonify({
            'response': result['response'],
            'session_id': result['session_id']
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'An error occurred while processing your message'}), 500

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Chat endpoint with streaming response for better performance."""
    try:
        # Initialize RAG engine if not already done
        initialize_rag_engine()
        
        if not rag_engine:
            return jsonify({'error': 'RAG engine not initialized'}), 500
            
        # Handle JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create session ID
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        def generate():
            try:
                if not rag_engine:
                    yield f"data: {json.dumps({'error': 'RAG engine not available', 'done': True})}\n\n"
                    return
                    
                # Get relevant documents and build prompt
                relevant_docs = rag_engine.retrieve_relevant_documents(user_message)
                context = rag_engine.format_context(relevant_docs)
                conversation_history = rag_engine.memory.get_conversation_history(session_id)
                prompt = rag_engine.build_prompt(user_message, context, conversation_history)
                
                # Stream the response
                full_response = ""
                for chunk in rag_engine.generate_response_stream(prompt):
                    full_response += chunk
                    # Send each chunk immediately with flush
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # Add to memory
                rag_engine.memory.add_message(session_id, "user", user_message)
                rag_engine.memory.add_message(session_id, "assistant", full_response)
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': f'Error: {str(e)}', 'done': True})}\n\n"
        
        return Response(generate(), 
                       mimetype='text/event-stream',
                       headers={
                           'Cache-Control': 'no-cache',
                           'Connection': 'keep-alive',
                           'Access-Control-Allow-Origin': '*'
                       })
        
    except Exception as e:
        print(f"Error in streaming chat endpoint: {e}")
        return jsonify({'error': 'An error occurred while processing your message'}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history."""
    try:
        session_id = session.get('session_id')
        if session_id and rag_engine:
            rag_engine.clear_conversation(session_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error clearing conversation: {e}")
        return jsonify({'error': 'Failed to clear conversation'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

@app.route('/test')
def test_streaming():
    """Test streaming page."""
    return render_template('test_streaming.html')

if __name__ == '__main__':
    print("Starting Jozef Neo-Latin Studies Chatbot...")
    print(f"Server will run on http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
