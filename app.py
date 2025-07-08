"""
Flask web application for the Jozef Neo-Latin Studies Chatbot.
Features a Renaissance-inspired Bootstrap interface.
"""

from flask import Flask, render_template, request, jsonify, session
import uuid
import config
from src.rag_engine import RAGEngine
from src.speech_service import SpeechService
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize RAG engine and speech service
rag_engine = None
speech_service = None

def initialize_rag_engine():
    """Initialize the RAG engine."""
    global rag_engine
    if rag_engine is None:
        print("Initializing RAG engine...")
        rag_engine = RAGEngine()
        print("RAG engine initialized.")

def initialize_speech_service():
    """Initialize the speech service."""
    global speech_service
    if speech_service is None:
        print("Initializing speech service...")
        speech_service = SpeechService()
        print("Speech service initialized.")

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
        
        data = request.json
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
            'sources': result['sources'],
            'session_id': result['session_id']
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
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

@app.route('/process_documents', methods=['POST'])
def process_documents():
    """Process PDF documents."""
    try:
        initialize_rag_engine()
        success = rag_engine.process_documents()
        if success:
            return jsonify({'status': 'success', 'message': 'Documents processed successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to process documents'}), 500
    except Exception as e:
        print(f"Error processing documents: {e}")
        return jsonify({'error': 'An error occurred while processing documents'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio using Whisper."""
    try:
        # Initialize speech service if not already done
        initialize_speech_service()
        
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        content_type = audio_file.content_type or 'audio/wav'
        
        # Validate audio format
        if not speech_service.validate_audio_format(audio_data):
            # Try to process anyway as Whisper is quite robust
            print(f"Warning: Audio format validation failed for {content_type}")
        
        # Transcribe audio
        result = speech_service.transcribe_audio(audio_data, content_type)
        
        if result['success']:
            return jsonify({
                'success': True,
                'transcript': result['transcript'],
                'confidence': result['confidence'],
                'language': result['language'],
                'duration': result.get('duration', 0.0)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Transcription failed')
            }), 500
            
    except Exception as e:
        print(f"Error in transcribe endpoint: {e}")
        return jsonify({'error': 'An error occurred during transcription'}), 500

@app.route('/speech/formats')
def get_supported_formats():
    """Get supported audio formats for speech recognition."""
    try:
        initialize_speech_service()
        return jsonify({
            'formats': speech_service.get_supported_formats(),
            'preferred': 'audio/wav'
        })
    except Exception as e:
        print(f"Error getting supported formats: {e}")
        return jsonify({'error': 'Could not get supported formats'}), 500

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
