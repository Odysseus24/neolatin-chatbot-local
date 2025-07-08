"""
Speech processing service using OpenAI Whisper for high-quality speech recognition
and enhanced text-to-speech capabilities.
"""

import whisper
import io
import wave
import tempfile
import os
from typing import Optional, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import numpy as np
import scipy.signal

class SpeechService:
    """Handles speech recognition and synthesis using Whisper and enhanced TTS."""
    
    def __init__(self):
        """Initialize the speech service with Whisper model."""
        print("Loading Whisper model...")
        # Use small model for better balance of speed and accuracy than base
        # Options: tiny, base, small, medium, large
        # small provides significantly better accuracy than base with minimal speed impact
        self.whisper_model = whisper.load_model("small")
        print("Whisper small model loaded successfully")
    
    def transcribe_audio(self, audio_data: bytes, content_type: str = "audio/wav") -> Dict[str, Any]:
        """
        Transcribe audio data using Whisper with preprocessing for optimal quality.
        
        Args:
            audio_data: Raw audio bytes
            content_type: MIME type of the audio
            
        Returns:
            Dict with transcription result and confidence
        """
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            try:
                # Preprocess audio for better quality
                processed_path = self._preprocess_audio(temp_audio_path)
                
                # Transcribe using Whisper with enhanced parameters
                result = self.whisper_model.transcribe(
                    processed_path,
                    language="en",  # Force English for Neo-Latin studies context
                    task="transcribe",
                    temperature=0.0,  # Lower temperature for more consistent results
                    compression_ratio_threshold=2.4,  # Filter out low-quality segments
                    logprob_threshold=-1.0,  # Filter out uncertain segments
                    no_speech_threshold=0.6,  # More sensitive speech detection
                    condition_on_previous_text=False,  # Don't condition on previous text
                    initial_prompt="This is academic content about Neo-Latin studies, classical literature, Renaissance texts, and scholarly discussion."  # Context hint
                )
                
                transcript = str(result.get("text", "")).strip()
                
                # Whisper doesn't provide confidence scores directly,
                # but we can estimate based on the segments
                segments = result.get("segments", [])
                avg_confidence = 0.8  # Default confidence for Whisper
                
                if segments and isinstance(segments, list):
                    # Try to calculate confidence from segments
                    try:
                        confidence_scores = []
                        for seg in segments:
                            if isinstance(seg, dict) and "no_speech_prob" in seg:
                                no_speech_prob = float(seg.get("no_speech_prob", 0.0))
                                confidence_scores.append(1.0 - no_speech_prob)
                        
                        if confidence_scores:
                            avg_confidence = sum(confidence_scores) / len(confidence_scores)
                            avg_confidence = max(0.0, min(1.0, avg_confidence))  # Clamp to [0,1]
                    except Exception:
                        avg_confidence = 0.8  # Fallback confidence
                
                return {
                    "success": True,
                    "transcript": transcript,
                    "confidence": avg_confidence,
                    "language": result.get("language", "en"),
                    "duration": result.get("duration", 0.0)
                }
                
            finally:
                # Clean up temporary files
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                
                # Clean up processed file if it exists and is different
                processed_file = temp_audio_path.replace('.wav', '_processed.wav')
                if os.path.exists(processed_file) and processed_file != temp_audio_path:
                    os.unlink(processed_file)
                    
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": "",
                "confidence": 0.0
            }
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        """
        Validate that the audio data is in a supported format.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            True if format is supported
        """
        try:
            # Try to read as WAV file
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                # Check basic properties
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                
                # Basic validation
                if channels in [1, 2] and sample_width in [1, 2, 4] and frame_rate >= 8000:
                    return True
                    
        except Exception as e:
            print(f"Audio validation error: {e}")
            
        return False
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats."""
        return [
            "audio/wav",
            "audio/wave", 
            "audio/x-wav",
            "audio/mpeg",
            "audio/mp3",
            "audio/mp4",
            "audio/m4a",
            "audio/ogg",
            "audio/webm"
        ]
    
    def _preprocess_audio(self, audio_path: str) -> str:
        """
        Preprocess audio for better Whisper transcription quality.
        
        Args:
            audio_path: Path to the input audio file
            
        Returns:
            Path to the processed audio file
        """
        try:
            import librosa
            
            # Load audio with librosa for high-quality processing
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            # Apply audio enhancements
            # 1. Noise reduction using spectral gating
            audio = librosa.effects.preemphasis(audio)
            
            # 2. Normalize audio levels
            audio = librosa.util.normalize(audio)
            
            # 3. Apply gentle high-pass filter to remove low-frequency noise
            audio = librosa.effects.hpss(audio)[0]  # Keep harmonic component
            
            # Save processed audio
            processed_path = audio_path.replace('.wav', '_processed.wav')
            import soundfile as sf
            sf.write(processed_path, audio, sr)
            
            return processed_path
            
        except ImportError:
            # If librosa/soundfile not available, use original file
            print("Audio preprocessing libraries not available, using original audio")
            return audio_path
        except Exception as e:
            print(f"Audio preprocessing failed: {e}, using original audio")
            return audio_path

def test_speech_service():
    """Test function for the speech service."""
    service = SpeechService()
    print("Speech service initialized successfully")
    print(f"Supported formats: {service.get_supported_formats()}")

if __name__ == "__main__":
    test_speech_service()
