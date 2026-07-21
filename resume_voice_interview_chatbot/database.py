"""
Database Module
===============
Handles all SQLite database operations for user management, 
interview history, and data persistence.
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from loguru import logger

import config


class Database:
    """Main database handler class."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        self.db_path = db_path or config.db_config.path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=config.db_config.timeout,
            check_same_thread=config.db_config.check_same_thread
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    last_login TIMESTAMP
                )
            """)
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    full_name TEXT,
                    phone TEXT,
                    linkedin_url TEXT,
                    github_url TEXT,
                    portfolio_url TEXT,
                    bio TEXT,
                    target_companies TEXT,  -- JSON array
                    target_roles TEXT,  -- JSON array
                    experience_years INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Resumes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    parsed_data TEXT,  -- JSON
                    extracted_skills TEXT,  -- JSON
                    analysis TEXT,  -- JSON
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Interviews table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    resume_id INTEGER,
                    company_mode TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, abandoned
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_questions INTEGER DEFAULT 0,
                    current_question_index INTEGER DEFAULT 0,
                    overall_score REAL,
                    hr_score REAL,
                    technical_score REAL,
                    communication_score REAL,
                    project_score REAL,
                    confidence_score REAL,
                    resume_quality_score REAL,
                    interview_readiness REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL
                )
            """)
            
            # Questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interview_id INTEGER NOT NULL,
                    question_number INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    difficulty TEXT DEFAULT 'medium',
                    is_followup BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
                )
            """)
            
            # Answers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    answer_text TEXT,
                    audio_path TEXT,
                    duration_seconds REAL,
                    evaluation TEXT,  -- JSON
                    score REAL,
                    strengths TEXT,  -- JSON array
                    weaknesses TEXT,  -- JSON array
                    improvement_tips TEXT,  -- JSON array
                    followup_question TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
                )
            """)
            
            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interview_id INTEGER NOT NULL,
                    report_data TEXT,  -- JSON
                    pdf_path TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
                )
            """)
            
            # Password reset tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interviews_user ON interviews(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_interview ON questions(interview_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_answers_question ON answers(question_id)")
            
            logger.info("Database initialized successfully")
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return pwd_hash.hex(), salt
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username: str, email: str, password: str) -> int:
        """Create a new user account."""
        password_hash, salt = self.hash_password(password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, salt))
            
            user_id = cursor.lastrowid
            
            # Create empty profile
            cursor.execute("""
                INSERT INTO user_profiles (user_id)
                VALUES (?)
            """, (user_id,))
            
            logger.info(f"User created: {username}")
            return user_id
    
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if valid."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users 
                WHERE (username = ? OR email = ?) AND is_active = 1
            """, (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            
            if user:
                password_hash, _ = self.hash_password(password, user['salt'])
                
                if password_hash == user['password_hash']:
                    # Update last login
                    cursor.execute("""
                        UPDATE users SET last_login = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (user['id'],))
                    
                    logger.info(f"User authenticated: {username_or_email}")
                    return dict(user)
            
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update user password."""
        password_hash, salt = self.hash_password(new_password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET password_hash = ?, salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (password_hash, salt, user_id))
            
            logger.info(f"Password updated for user_id: {user_id}")
            return cursor.rowcount > 0
    
    def create_password_reset_token(self, user_id: int) -> str:
        """Create password reset token."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now().timestamp() + 3600  # 1 hour
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, token, expires_at))
        
        return token
    
    def validate_reset_token(self, token: str) -> Optional[int]:
        """Validate password reset token and return user_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id FROM password_reset_tokens
                WHERE token = ? AND used = 0 AND expires_at > ?
            """, (token, datetime.now().timestamp()))
            
            result = cursor.fetchone()
            
            if result:
                cursor.execute("""
                    UPDATE password_reset_tokens SET used = 1
                    WHERE token = ?
                """, (token,))
                
                return result['user_id']
            
            return None
    
    # ==================== PROFILE OPERATIONS ====================
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            profile = cursor.fetchone()
            return dict(profile) if profile else None
    
    def update_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile."""
        fields = []
        values = []
        
        for key, value in profile_data.items():
            if key in ['target_companies', 'target_roles'] and isinstance(value, list):
                value = json.dumps(value)
            fields.append(f"{key} = ?")
            values.append(value)
        
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE user_profiles SET {', '.join(fields)}
                WHERE user_id = ?
            """, values)
            
            return cursor.rowcount > 0
    
    # ==================== RESUME OPERATIONS ====================
    
    def save_resume(self, user_id: int, filename: str, file_path: str, 
                   file_type: str, parsed_data: Dict, 
                   extracted_skills: List[str], analysis: Dict) -> int:
        """Save resume record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resumes (
                    user_id, filename, file_path, file_type,
                    parsed_data, extracted_skills, analysis
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, filename, file_path, file_type,
                json.dumps(parsed_data),
                json.dumps(extracted_skills),
                json.dumps(analysis)
            ))
            
            logger.info(f"Resume saved for user_id: {user_id}")
            return cursor.lastrowid
    
    def get_user_resumes(self, user_id: int) -> List[Dict]:
        """Get all resumes for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM resumes WHERE user_id = ?
                ORDER BY uploaded_at DESC
            """, (user_id,))
            
            resumes = cursor.fetchall()
            return [dict(r) for r in resumes]
    
    def get_resume_by_id(self, resume_id: int) -> Optional[Dict]:
        """Get resume by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
            resume = cursor.fetchone()
            
            if resume:
                resume_dict = dict(resume)
                # Parse JSON fields
                if resume_dict.get('parsed_data'):
                    resume_dict['parsed_data'] = json.loads(resume_dict['parsed_data'])
                if resume_dict.get('extracted_skills'):
                    resume_dict['extracted_skills'] = json.loads(resume_dict['extracted_skills'])
                if resume_dict.get('analysis'):
                    resume_dict['analysis'] = json.loads(resume_dict['analysis'])
                return resume_dict
            
            return None
    
    def delete_resume(self, resume_id: int) -> bool:
        """Delete resume record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            return cursor.rowcount > 0
    
    # ==================== INTERVIEW OPERATIONS ====================
    
    def create_interview(self, user_id: int, resume_id: Optional[int],
                         company_mode: str) -> int:
        """Create new interview session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interviews (user_id, resume_id, company_mode, status)
                VALUES (?, ?, ?, 'pending')
            """, (user_id, resume_id, company_mode))
            
            logger.info(f"Interview created for user_id: {user_id}, mode: {company_mode}")
            return cursor.lastrowid
    
    def get_interview(self, interview_id: int) -> Optional[Dict]:
        """Get interview by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
            interview = cursor.fetchone()
            return dict(interview) if interview else None
    
    def update_interview_status(self, interview_id: int, status: str) -> bool:
        """Update interview status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status == 'in_progress':
                cursor.execute("""
                    UPDATE interviews SET status = ?, started_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, interview_id))
            elif status == 'completed':
                cursor.execute("""
                    UPDATE interviews SET status = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, interview_id))
            else:
                cursor.execute("""
                    UPDATE interviews SET status = ?
                    WHERE id = ?
                """, (status, interview_id))
            
            return cursor.rowcount > 0
    
    def update_interview_scores(self, interview_id: int, scores: Dict) -> bool:
        """Update interview scores."""
        fields = []
        values = []
        
        for key, value in scores.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(interview_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE interviews SET {', '.join(fields)}
                WHERE id = ?
            """, values)
            
            return cursor.rowcount > 0
    
    def get_user_interviews(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get interview history for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM interviews WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            interviews = cursor.fetchall()
            return [dict(i) for i in interviews]
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total interviews
            cursor.execute("""
                SELECT COUNT(*) as total FROM interviews WHERE user_id = ?
            """, (user_id,))
            total = cursor.fetchone()['total']
            
            # Completed interviews
            cursor.execute("""
                SELECT COUNT(*) as completed FROM interviews 
                WHERE user_id = ? AND status = 'completed'
            """, (user_id,))
            completed = cursor.fetchone()['completed']
            
            # Average score
            cursor.execute("""
                SELECT AVG(overall_score) as avg_score FROM interviews
                WHERE user_id = ? AND status = 'completed' AND overall_score IS NOT NULL
            """, (user_id,))
            avg_score = cursor.fetchone()['avg_score']
            
            # Resumes count
            cursor.execute("""
                SELECT COUNT(*) as resumes FROM resumes WHERE user_id = ?
            """, (user_id,))
            resumes_count = cursor.fetchone()['resumes']
            
            return {
                'total_interviews': total,
                'completed_interviews': completed,
                'average_score': round(avg_score, 2) if avg_score else 0,
                'total_resumes': resumes_count
            }
    
    # ==================== QUESTION OPERATIONS ====================
    
    def save_question(self, interview_id: int, question_number: int,
                     category: str, question_text: str, 
                     difficulty: str = 'medium',
                     is_followup: bool = False) -> int:
        """Save question to database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO questions (
                    interview_id, question_number, category,
                    question_text, difficulty, is_followup
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (interview_id, question_number, category, 
                  question_text, difficulty, is_followup))
            
            return cursor.lastrowid
    
    def get_interview_questions(self, interview_id: int) -> List[Dict]:
        """Get all questions for an interview."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM questions WHERE interview_id = ?
                ORDER BY question_number, is_followup
            """, (interview_id,))
            
            questions = cursor.fetchall()
            return [dict(q) for q in questions]
    
    # ==================== ANSWER OPERATIONS ====================
    
    def save_answer(self, question_id: int, answer_text: str,
                   audio_path: Optional[str] = None,
                   duration_seconds: Optional[float] = None,
                   evaluation: Optional[Dict] = None,
                   score: Optional[float] = None,
                   strengths: Optional[List[str]] = None,
                   weaknesses: Optional[List[str]] = None,
                   improvement_tips: Optional[List[str]] = None,
                   followup_question: Optional[str] = None) -> int:
        """Save answer and evaluation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO answers (
                    question_id, answer_text, audio_path, duration_seconds,
                    evaluation, score, strengths, weaknesses,
                    improvement_tips, followup_question
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                question_id, answer_text, audio_path, duration_seconds,
                json.dumps(evaluation) if evaluation else None,
                score,
                json.dumps(strengths) if strengths else None,
                json.dumps(weaknesses) if weaknesses else None,
                json.dumps(improvement_tips) if improvement_tips else None,
                followup_question
            ))
            
            return cursor.lastrowid
    
    def get_question_answer(self, question_id: int) -> Optional[Dict]:
        """Get answer for a question."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.*, a.*, q.question_text as question
                FROM questions q
                LEFT JOIN answers a ON q.id = a.question_id
                WHERE q.id = ?
            """, (question_id,))
            
            result = cursor.fetchone()
            
            if result:
                result_dict = dict(result)
                # Parse JSON fields
                if result_dict.get('evaluation'):
                    result_dict['evaluation'] = json.loads(result_dict['evaluation'])
                if result_dict.get('strengths'):
                    result_dict['strengths'] = json.loads(result_dict['strengths'])
                if result_dict.get('weaknesses'):
                    result_dict['weaknesses'] = json.loads(result_dict['weaknesses'])
                if result_dict.get('improvement_tips'):
                    result_dict['improvement_tips'] = json.loads(result_dict['improvement_tips'])
                return result_dict
            
            return None
    
    def get_interview_answers(self, interview_id: int) -> List[Dict]:
        """Get all answers for an interview."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.*, a.* FROM questions q
                LEFT JOIN answers a ON q.id = a.question_id
                WHERE q.interview_id = ?
                ORDER BY q.question_number
            """, (interview_id,))
            
            results = cursor.fetchall()
            answers = []
            
            for row in results:
                answer_dict = dict(row)
                # Parse JSON fields
                if answer_dict.get('evaluation'):
                    answer_dict['evaluation'] = json.loads(answer_dict['evaluation'])
                if answer_dict.get('strengths'):
                    answer_dict['strengths'] = json.loads(answer_dict['strengths'])
                if answer_dict.get('weaknesses'):
                    answer_dict['weaknesses'] = json.loads(answer_dict['weaknesses'])
                if answer_dict.get('improvement_tips'):
                    answer_dict['improvement_tips'] = json.loads(answer_dict['improvement_tips'])
                answers.append(answer_dict)
            
            return answers
    
    # ==================== REPORT OPERATIONS ====================
    
    def save_report(self, interview_id: int, report_data: Dict, pdf_path: Optional[str] = None) -> int:
        """Save interview report."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reports (interview_id, report_data, pdf_path)
                VALUES (?, ?, ?)
            """, (interview_id, json.dumps(report_data), pdf_path))
            
            logger.info(f"Report saved for interview_id: {interview_id}")
            return cursor.lastrowid
    
    def get_interview_report(self, interview_id: int) -> Optional[Dict]:
        """Get report for an interview."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reports WHERE interview_id = ?
            """, (interview_id,))
            
            report = cursor.fetchone()
            
            if report:
                report_dict = dict(report)
                if report_dict.get('report_data'):
                    report_dict['report_data'] = json.loads(report_dict['report_data'])
                return report_dict
            
            return None


# Global database instance
db = Database()
