"""
Voice Input Module
=================
Handles speech-to-text conversion for interview answers.
Supports Whisper API and Google Speech Recognition.
"""

import io
import wave
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger

import config


class VoiceInput:
    """Handles speech-to-text conversion."""
    
    def __init__(self, model_size: str = "base"):
        """Initialize voice input handler."""
        self.model_size = model_size
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """Initialize Whisper model."""
        try:
            from faster_whisper import WhisperModel
            
            device = "cpu" if config.whisper_config.device == "cpu" else "cuda"
            compute_type = config.whisper_config.compute_type
            
            self.model = WhisperModel(
                config.whisper_config.model_size,
                device=device,
                compute_type=compute_type
            )
            logger.info(f"Whisper model loaded: {config.whisper_config.model_size}")
            
        except ImportError:
            logger.warning("faster-whisper not installed, using fallback")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
    
    def transcribe_audio(
        self,
        audio_path: Path,
        language: str = "en"
    ) -> Tuple[str, float]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: en)
            
        Returns:
            Tuple of (transcribed text, confidence score)
        """
        if self.model is None:
            return self._fallback_transcribe(audio_path)
        
        try:
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language,
                beam_size=5,
                vad_filter=True
            )
            
            full_text = []
            total_duration = 0
            
            for segment in segments:
                full_text.append(segment.text)
                total_duration += segment.end - segment.start
            
            transcription = " ".join(full_text).strip()
            confidence = info.language_probability
            
            logger.info(f"Transcription: {transcription[:100]}...")
            return transcription, confidence
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return self._fallback_transcribe(audio_path)
    
    def transcribe_audio_data(
        self,
        audio_data: bytes,
        format: str = "wav",
        language: str = "en"
    ) -> Tuple[str, float]:
        """
        Transcribe audio data directly.
        
        Args:
            audio_data: Raw audio bytes
            format: Audio format (wav, mp3, etc.)
            language: Language code
            
        Returns:
            Tuple of (transcribed text, confidence score)
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as f:
            f.write(audio_data)
            temp_path = Path(f.name)
        
        try:
            return self.transcribe_audio(temp_path, language)
        finally:
            # Clean up
            if temp_path.exists():
                temp_path.unlink()
    
    def _fallback_transcribe(self, audio_path: Path) -> Tuple[str, float]:
        """Fallback transcription using SpeechRecognition."""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(str(audio_path)) as source:
                audio = recognizer.record(source)
            
            # Try Google Speech Recognition
            text = recognizer.recognize_google(audio, language='en-IN')  # Indian English
            return text, 0.8
            
        except Exception as e:
            logger.error(f"Fallback transcription failed: {e}")
            return "", 0.0
    
    def is_speech_detected(
        self,
        audio_path: Path,
        threshold: float = 0.01,
        silence_duration: float = 2.0
    ) -> bool:
        """
        Detect if audio contains speech.
        
        Args:
            audio_path: Path to audio file
            threshold: Energy threshold for speech detection
            silence_duration: Seconds of silence to consider as end
            
        Returns:
            True if speech is detected
        """
        try:
            import numpy as np
            
            # Read WAV file
            with wave.open(str(audio_path), 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
            
            # Convert to numpy array
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            # Calculate energy
            energy = np.abs(audio_data).mean()
            
            return energy > threshold * 32768
            
        except Exception as e:
            logger.warning(f"Speech detection failed: {e}")
            return True  # Assume speech detected if check fails
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds."""
        try:
            with wave.open(str(audio_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                return frames / float(rate)
        except Exception as e:
            logger.warning(f"Duration check failed: {e}")
            return 0.0


class AudioRecorder:
    """Records audio from microphone."""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """Initialize audio recorder."""
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames = []
        self.recording = False
        self.stream = None
    
    def start_recording(self) -> bool:
        """Start recording audio."""
        try:
            import pyaudio
            
            self.audio = pyaudio.PyAudio()
            self.frames = []
            
            # Try to get input device
            device_info = self.audio.get_default_input_device_info()
            
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_info['index'],
                frames_per_buffer=1024
            )
            
            self.recording = True
            logger.info("Recording started")
            return True
            
        except ImportError:
            logger.error("pyaudio not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> Optional[bytes]:
        """Stop recording and return audio data."""
        if not self.recording:
            return None
        
        try:
            self.recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            
            # Save to bytes
            audio_data = self._save_to_wav_bytes()
            
            if self.audio:
                self.audio.terminate()
            
            logger.info("Recording stopped")
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None
    
    def _save_to_wav_bytes(self) -> bytes:
        """Save recorded frames to WAV format."""
        import array
        
        # Convert frames to bytes
        audio_bytes = b''.join(self.frames)
        
        # Create WAV file in memory
        import struct
        
        num_channels = self.channels
        sample_width = 2  # 16-bit
        frame_rate = self.sample_rate
        num_frames = len(audio_bytes) // sample_width
        
        # WAV header
        header = struct.pack(
            '<4sI4s',
            b'RIFF',
            36 + len(audio_bytes),
            b'WAVE'
        )
        
        fmt_chunk = struct.pack(
            '<4sIHHIIHH',
            b'fmt ',
            16,  # Chunk size
            1,   # Audio format (PCM)
            num_channels,
            frame_rate,
            frame_rate * num_channels * sample_width,  # Byte rate
            num_channels * sample_width,  # Block align
            sample_width * 8  # Bits per sample
        )
        
        data_chunk = struct.pack(
            '<4sI',
            b'data',
            len(audio_bytes)
        )
        
        return header + fmt_chunk + data_chunk + audio_bytes
    
    def save_to_file(self, audio_data: bytes, output_path: Path) -> bool:
        """Save audio data to file."""
        try:
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            logger.info(f"Audio saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False


def record_and_transcribe(
    duration: int = 30,
    language: str = "en"
) -> Tuple[str, float, float]:
    """
    Convenience function to record and transcribe.
    
    Args:
        duration: Maximum recording duration in seconds
        language: Language code
        
    Returns:
        Tuple of (transcription, confidence, audio_duration)
    """
    recorder = AudioRecorder()
    voice_input = VoiceInput()
    
    # Start recording
    if not recorder.start_recording():
        return "", 0.0, 0.0
    
    # Record for specified duration
    import time
    start_time = time.time()
    recorder.frames = []
    
    try:
        import pyaudio
        
        while time.time() - start_time < duration and recorder.recording:
            try:
                data = recorder.stream.read(1024)
                recorder.frames.append(data)
            except:
                break
            
    except ImportError:
        # If pyaudio not available, wait
        time.sleep(duration)
    
    # Stop and get audio data
    audio_data = recorder.stop_recording()
    
    if audio_data:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = Path(f.name)
        
        try:
            # Transcribe
            transcription, confidence = voice_input.transcribe_audio(temp_path)
            duration_seconds = voice_input.get_audio_duration(temp_path)
            return transcription, confidence, duration_seconds
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    return "", 0.0, 0.0
