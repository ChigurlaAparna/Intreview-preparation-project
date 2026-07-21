"""
Voice Output Module
==================
Handles text-to-speech conversion for reading questions aloud.
Uses Edge TTS for natural voice synthesis.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional, List, Dict
from loguru import logger

import config


class VoiceOutput:
    """Handles text-to-speech conversion."""
    
    def __init__(self):
        """Initialize voice output handler."""
        self.voice = config.edge_tts_config.voice
        self.rate = config.edge_tts_config.rate
        self.volume = config.edge_tts_config.volume
        self.pitch = config.edge_tts_config.pitch
        self._temp_files = []
    
    async def _speak_async(self, text: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """Async method to convert text to speech."""
        try:
            import edge_tts
            
            if output_path is None:
                output_path = Path(tempfile.mktemp(suffix=".mp3"))
            
            communicate = edge_tts.Communicate(
                text,
                self.voice,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch
            )
            
            await communicate.save(str(output_path))
            self._temp_files.append(output_path)
            
            return output_path
            
        except ImportError:
            logger.error("edge-tts not installed")
            return None
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None
    
    def speak(self, text: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert to speech
            output_path: Optional output file path
            
        Returns:
            Path to generated audio file
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._speak_async(text, output_path))
    
    async def _speak_ssml_async(
        self,
        ssml_text: str,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Async method to convert SSML to speech."""
        try:
            import edge_tts
            
            if output_path is None:
                output_path = Path(tempfile.mktemp(suffix=".mp3"))
            
            communicate = edge_tts.Communicate()
            await communicate.save_ssml(ssml_text, str(output_path))
            
            self._temp_files.append(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"SSML TTS failed: {e}")
            return None
    
    def speak_ssml(self, ssml_text: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """Convert SSML to speech."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._speak_ssml_async(ssml_text, output_path))
    
    def generate_introduction(self, candidate_name: str, company_mode: str) -> Optional[Path]:
        """Generate introduction speech."""
        from prompts import VOICE_INTERVIEW_INTRO
        
        intro_text = VOICE_INTERVIEW_INTRO.format(
            name=candidate_name,
            company_mode=company_mode
        )
        
        return self.speak(intro_text)
    
    def generate_question_speech(
        self,
        question_number: int,
        question_text: str,
        category: str,
        difficulty: str
    ) -> Optional[Path]:
        """Generate speech for interview question with natural phrasing."""
        # Add question number and category context
        difficulty_text = {
            'easy': "Let's start with a straightforward question.",
            'medium': "Here's a question to test your knowledge.",
            'hard': "This is a more challenging question. Take your time."
        }
        
        category_text = {
            'hr': "about your background and experience",
            'technical': "to assess your technical knowledge",
            'programming': "to evaluate your coding skills",
            'projects': "about your project experience",
            'sql': "on database concepts",
            'python': "about Python programming",
            'machine_learning': "on machine learning concepts",
            'deep_learning': "about deep learning",
            'nlp': "on natural language processing",
            'dbms': "on database management",
            'operating_system': "about operating systems",
            'oop': "on object-oriented programming",
            'behavioral': "to understand your approach to situations",
            'situational': "hypothetical scenario question"
        }
        
        # Build natural speech
        speech_parts = []
        
        if question_number == 1:
            speech_parts.append("Now, let's begin the interview.")
        
        speech_parts.append(f"Question number {question_number}.")
        speech_parts.append(difficulty_text.get(difficulty, ""))
        speech_parts.append(f"This question is {category_text.get(category, '')}.")
        speech_parts.append(question_text)
        
        speech_text = " ".join(speech_parts)
        
        return self.speak(speech_text)
    
    def generate_transition(self) -> Optional[str]:
        """Get a transition phrase to speak."""
        from prompts import VOICE_TRANSITION_PHRASES
        import random
        return random.choice(VOICE_TRANSITION_PHRASES)
    
    def generate_encouragement(self, message: str) -> Optional[Path]:
        """Generate encouragement speech."""
        return self.speak(message)
    
    def generate_feedback_summary(
        self,
        score: float,
        strengths: List[str],
        improvements: List[str]
    ) -> Optional[Path]:
        """Generate summary feedback speech."""
        speech_parts = [
            "Here's a summary of your interview performance.",
            f"Your overall score is {score:.1f} out of 10."
        ]
        
        if strengths:
            speech_parts.append("Your key strengths were:")
            for strength in strengths[:3]:
                speech_parts.append(f"- {strength}")
        
        if improvements:
            speech_parts.append("Areas for improvement include:")
            for improvement in improvements[:3]:
                speech_parts.append(f"- {improvement}")
        
        speech_parts.append("Thank you for participating in this interview.")
        
        return self.speak(" ".join(speech_parts))
    
    def set_voice(self, voice: str) -> bool:
        """Set the voice for TTS."""
        valid_voices = [
            'en-US-AriaNeural',
            'en-US-JennyNeural',
            'en-US-GuyNeural',
            'en-US-SaraNeural',
            'en-IN-NeerjaExpressive',
            'en-IN-PrabhatNeural',
            'en-GB-SoniaNeural',
            'en-AU-NatashaNeural'
        ]
        
        if voice in valid_voices:
            self.voice = voice
            return True
        return False
    
    def set_rate(self, rate: str) -> bool:
        """Set speech rate (e.g., '+10%', '-5%')."""
        try:
            # Validate format
            if rate.endswith('%'):
                value = int(rate[:-1])
                if -100 <= value <= 100:
                    self.rate = rate
                    return True
        except ValueError:
            pass
        return False
    
    def set_pitch(self, pitch: str) -> bool:
        """Set speech pitch (e.g., '+5Hz', '-10Hz')."""
        try:
            if pitch.endswith('Hz'):
                value = int(pitch[:-2])
                if -50 <= value <= 50:
                    self.pitch = pitch
                    return True
        except ValueError:
            pass
        return False
    
    def cleanup(self):
        """Clean up temporary audio files."""
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")
        
        self._temp_files = []
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()


class VoiceConfig:
    """Manages voice configuration options."""
    
    VOICES = {
        'en-US-AriaNeural': {'name': 'Aria', 'gender': 'Female', 'accent': 'American'},
        'en-US-JennyNeural': {'name': 'Jenny', 'gender': 'Female', 'accent': 'American'},
        'en-US-GuyNeural': {'name': 'Guy', 'gender': 'Male', 'accent': 'American'},
        'en-US-SaraNeural': {'name': 'Sara', 'gender': 'Female', 'accent': 'American'},
        'en-IN-NeerjaExpressive': {'name': 'Neerja', 'gender': 'Female', 'accent': 'Indian'},
        'en-IN-PrabhatNeural': {'name': 'Prabhat', 'gender': 'Male', 'accent': 'Indian'},
        'en-GB-SoniaNeural': {'name': 'Sonia', 'gender': 'Female', 'accent': 'British'},
        'en-AU-NatashaNeural': {'name': 'Natasha', 'gender': 'Female', 'accent': 'Australian'},
    }
    
    RATE_OPTIONS = ['-20%', '-10%', '+0%', '+10%', '+20%']
    PITCH_OPTIONS = ['-10Hz', '-5Hz', '+0Hz', '+5Hz', '+10Hz']
    
    @classmethod
    def get_available_voices(cls) -> List[Dict]:
        """Get list of available voices."""
        return [
            {'id': voice_id, **info}
            for voice_id, info in cls.VOICES.items()
        ]
    
    @classmethod
    def get_voice_info(cls, voice_id: str) -> Optional[Dict]:
        """Get information about a specific voice."""
        return cls.VOICES.get(voice_id)


def speak_text(text: str, output_path: Optional[Path] = None) -> Optional[Path]:
    """Convenience function to speak text."""
    voice = VoiceOutput()
    return voice.speak(text, output_path)


def speak_question(
    question_number: int,
    question_text: str,
    category: str,
    difficulty: str
) -> Optional[Path]:
    """Convenience function to speak a question."""
    voice = VoiceOutput()
    return voice.generate_question_speech(question_number, question_text, category, difficulty)
