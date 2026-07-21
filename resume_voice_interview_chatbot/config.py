"""
Configuration Module
===================
Centralizes all application settings, API keys, and environment variables.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).parent.absolute()

# Paths
UPLOAD_DIR = BASE_DIR / "uploads"
DATABASE_DIR = BASE_DIR / "database"
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
for directory in [UPLOAD_DIR, DATABASE_DIR, REPORTS_DIR, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    path: Path = DATABASE_DIR / "interview_bot.db"
    timeout: int = 30
    check_same_thread: bool = False


@dataclass
class GeminiConfig:
    """Google Gemini API configuration."""
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    model: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class WhisperConfig:
    """Whisper STT configuration."""
    model_size: str = "base"
    device: str = "cpu"  # Options: "cpu", "cuda"
    compute_type: str = "int8"


@dataclass
class EdgeTTSConfig:
    """Edge TTS configuration."""
    voice: str = "en-US-AriaNeural"  # Natural interviewer voice
    rate: str = "+0%"
    volume: str = "+0%"
    pitch: str = "+0Hz"


@dataclass
class InterviewConfig:
    """Interview session configuration."""
    max_questions: int = 25
    min_questions: int = 10
    time_per_question: int = 180  # seconds
    follow_up_probability: float = 0.4
    difficulty_increment: float = 0.15


@dataclass
class CompanyModes:
    """Company-specific interview styles."""
    TCS = {
        "name": "TCS",
        "style": "structured",
        "focus": ["aptitude", "communication", "basic_technical"],
        "question_count": 20,
        "difficulty": "medium"
    }
    
    INFOSYS = {
        "name": "Infosys",
        "style": "technical_deep",
        "focus": ["problem_solving", "coding", "algorithms"],
        "question_count": 18,
        "difficulty": "medium_to_hard"
    }
    
    ACCENTURE = {
        "name": "Accenture",
        "style": "project_based",
        "focus": ["project_experience", "client_facing", "agile"],
        "question_count": 22,
        "difficulty": "medium"
    }
    
    DELOITTE = {
        "name": "Deloitte",
        "style": "consulting",
        "focus": ["business_cases", "analytical", "communication"],
        "question_count": 20,
        "difficulty": "hard"
    }
    
    CAPGEMINI = {
        "name": "Capgemini",
        "style": "technical",
        "focus": ["technical_skills", "projects", "problem_solving"],
        "question_count": 18,
        "difficulty": "medium"
    }
    
    COGNIZANT = {
        "name": "Cognizant",
        "style": "corporate",
        "focus": ["communication", "adaptability", "technical"],
        "question_count": 20,
        "difficulty": "medium"
    }
    
    MICROSOFT = {
        "name": "Microsoft",
        "style": "product_development",
        "focus": ["coding", "system_design", "problem_solving"],
        "question_count": 25,
        "difficulty": "hard"
    }
    
    AMAZON = {
        "name": "Amazon",
        "style": "leadership_principles",
        "focus": ["behavioral", "system_design", "coding"],
        "question_count": 22,
        "difficulty": "hard"
    }
    
    GOOGLE = {
        "name": "Google",
        "style": "algorithmic",
        "focus": ["coding", "algorithms", "data_structures"],
        "question_count": 25,
        "difficulty": "very_hard"
    }


# Evaluation Categories
EVALUATION_CATEGORIES = [
    "technical_accuracy",
    "communication",
    "confidence",
    "fluency",
    "grammar",
    "completeness",
    "problem_solving",
    "domain_knowledge"
]

# Question Categories for Interview
QUESTION_CATEGORIES = [
    "hr",
    "technical",
    "programming",
    "projects",
    "sql",
    "python",
    "machine_learning",
    "deep_learning",
    "nlp",
    "dbms",
    "operating_system",
    "oop",
    "behavioral",
    "situational"
]

# Score Thresholds
SCORE_THRESHOLDS = {
    "excellent": 8.5,
    "good": 7.0,
    "average": 5.5,
    "below_average": 4.0
}


# Instantiate configs
db_config = DatabaseConfig()
gemini_config = GeminiConfig()
openai_config = OpenAIConfig()
whisper_config = WhisperConfig()
edge_tts_config = EdgeTTSConfig()
interview_config = InterviewConfig()
