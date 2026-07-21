"""
Utils Module
============
Utility functions for the interview chatbot.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def generate_session_id() -> str:
    """Generate unique session ID."""
    import uuid
    return str(uuid.uuid4())


def hash_string(text: str) -> str:
    """Generate hash for string."""
    return hashlib.sha256(text.encode()).hexdigest()


def format_duration(seconds: float) -> str:
    """Format seconds to readable duration."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    phone_pattern = r'(\+?91[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    return re.findall(phone_pattern, text)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple:
    """Validate password strength. Returns (is_valid, message)."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"


def convert_to_dict(obj: Any) -> Dict:
    """Convert object to dictionary."""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    elif hasattr(obj, '_asdict'):
        return obj._asdict()
    elif isinstance(obj, dict):
        return obj
    else:
        return {"value": obj}


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def flatten_list(nested_list: List[List]) -> List:
    """Flatten a nested list."""
    return [item for sublist in nested_list for item in sublist]


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage."""
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)


def get_score_color(score: float) -> str:
    """Get color based on score."""
    if score >= 8.0:
        return "green"
    elif score >= 6.0:
        return "orange"
    else:
        return "red"


def format_timestamp(timestamp: str, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format ISO timestamp to readable string."""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime(format_str)
    except (ValueError, TypeError):
        return timestamp


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special Unicode characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text.strip()


def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from text."""
    pattern = r'```[\s\S]*?```'
    return re.findall(pattern, text)


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate reading time in minutes."""
    word_count = len(text.split())
    return max(1, word_count // words_per_minute)


def create_directory_if_not_exists(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Get file extension."""
    return Path(filename).suffix.lower()


def is_pdf_file(filename: str) -> bool:
    """Check if file is PDF."""
    return get_file_extension(filename) == '.pdf'


def is_docx_file(filename: str) -> bool:
    """Check if file is DOCX."""
    return get_file_extension(filename) in ['.docx', '.doc']


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely dump object to JSON string."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return default


class ProgressTracker:
    """Track progress of interview or task."""
    
    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1) -> float:
        """Update progress and return percentage."""
        self.current = min(self.current + increment, self.total)
        return self.get_percentage()
    
    def get_percentage(self) -> float:
        """Get progress percentage."""
        if self.total == 0:
            return 0.0
        return round((self.current / self.total) * 100, 2)
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def estimate_remaining_time(self) -> float:
        """Estimate remaining time based on progress."""
        elapsed = self.get_elapsed_time()
        if self.current == 0:
            return 0.0
        
        rate = self.current / elapsed
        remaining = self.total - self.current
        
        return remaining / rate if rate > 0 else 0.0


class Logger:
    """Simple logger utility."""
    
    def __init__(self, name: str):
        self.name = name
    
    def info(self, message: str):
        """Log info message."""
        print(f"[INFO] {self.name}: {message}")
    
    def warning(self, message: str):
        """Log warning message."""
        print(f"[WARNING] {self.name}: {message}")
    
    def error(self, message: str):
        """Log error message."""
        print(f"[ERROR] {self.name}: {message}")
    
    def debug(self, message: str):
        """Log debug message."""
        print(f"[DEBUG] {self.name}: {message}")
