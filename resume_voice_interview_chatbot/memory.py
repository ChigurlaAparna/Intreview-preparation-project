"""
Memory Module
============
Manages interview conversation memory and state.
Tracks questions, answers, scores, and context for adaptive interviewing.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from loguru import logger

import config


@dataclass
class QuestionMemory:
    """Stores information about a question and its answer."""
    question_id: int
    question_text: str
    category: str
    difficulty: str
    answer: Optional[str] = None
    score: Optional[float] = None
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    followup_asked: bool = False
    followup_question: Optional[str] = None
    followup_answer: Optional[str] = None
    followup_score: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TopicAnalysis:
    """Analysis of performance in a specific topic."""
    topic: str
    questions_asked: int = 0
    total_score: float = 0.0
    strong_count: int = 0  # Score >= 7
    weak_count: int = 0     # Score < 6
    questions: List[int] = field(default_factory=list)
    
    @property
    def average_score(self) -> float:
        if self.questions_asked == 0:
            return 0.0
        return round(self.total_score / self.questions_asked, 2)
    
    @property
    def performance_status(self) -> str:
        if self.questions_asked == 0:
            return "not_asked"
        if self.average_score >= 7.5:
            return "strong"
        elif self.average_score >= 6.0:
            return "moderate"
        elif self.average_score >= 4.0:
            return "weak"
        else:
            return "struggling"


@dataclass
class InterviewMemory:
    """Complete interview session memory."""
    session_id: str
    user_id: int
    resume_data: Dict[str, Any]
    company_mode: str
    target_role: str
    questions: List[QuestionMemory] = field(default_factory=list)
    topic_analysis: Dict[str, TopicAnalysis] = field(default_factory=dict)
    current_difficulty: str = "medium"
    questions_asked: int = 0
    total_score: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "in_progress"  # pending, in_progress, paused, completed
    
    @property
    def average_score(self) -> float:
        if self.questions_asked == 0:
            return 0.0
        return round(self.total_score / self.questions_asked, 2)
    
    @property
    def progress_percentage(self) -> float:
        max_questions = config.interview_config.max_questions
        return min(100.0, round((self.questions_asked / max_questions) * 100, 1))
    
    @property
    def strong_topics(self) -> List[str]:
        return [
            topic for topic, analysis in self.topic_analysis.items()
            if analysis.performance_status == "strong"
        ]
    
    @property
    def weak_topics(self) -> List[str]:
        return [
            topic for topic, analysis in self.topic_analysis.items()
            if analysis.performance_status in ["weak", "struggling"]
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'resume_data': self.resume_data,
            'company_mode': self.company_mode,
            'target_role': self.target_role,
            'questions': [asdict(q) for q in self.questions],
            'topic_analysis': {k: asdict(v) for k, v in self.topic_analysis.items()},
            'current_difficulty': self.current_difficulty,
            'questions_asked': self.questions_asked,
            'total_score': self.total_score,
            'average_score': self.average_score,
            'progress_percentage': self.progress_percentage,
            'strong_topics': self.strong_topics,
            'weak_topics': self.weak_topics,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'status': self.status
        }


class InterviewMemoryManager:
    """Manages interview memory across sessions."""
    
    def __init__(self):
        """Initialize memory manager."""
        self.active_sessions: Dict[str, InterviewMemory] = {}
        self.session_history: Dict[int, List[str]] = {}  # user_id -> session_ids
    
    def create_session(
        self,
        session_id: str,
        user_id: int,
        resume_data: Dict[str, Any],
        company_mode: str,
        target_role: Optional[str] = None
    ) -> InterviewMemory:
        """
        Create a new interview session.
        
        Args:
            session_id: Unique session identifier
            user_id: User ID
            resume_data: Parsed resume data
            company_mode: Target company mode
            target_role: Target job role
            
        Returns:
            New InterviewMemory instance
        """
        # Determine target role from resume if not provided
        if not target_role:
            analysis = resume_data.get('analysis', {})
            target_role = analysis.get('target_role', 'Software Engineer')
        
        memory = InterviewMemory(
            session_id=session_id,
            user_id=user_id,
            resume_data=resume_data,
            company_mode=company_mode,
            target_role=target_role,
            started_at=datetime.now().isoformat(),
            status="in_progress"
        )
        
        self.active_sessions[session_id] = memory
        
        # Track in history
        if user_id not in self.session_history:
            self.session_history[user_id] = []
        self.session_history[user_id].append(session_id)
        
        logger.info(f"Created interview session: {session_id}")
        return memory
    
    def get_session(self, session_id: str) -> Optional[InterviewMemory]:
        """Get an active session."""
        return self.active_sessions.get(session_id)
    
    def get_or_create_session(
        self,
        session_id: str,
        user_id: int,
        resume_data: Dict[str, Any],
        company_mode: str,
        target_role: Optional[str] = None
    ) -> InterviewMemory:
        """Get existing session or create new one."""
        session = self.get_session(session_id)
        if session:
            return session
        return self.create_session(session_id, user_id, resume_data, company_mode, target_role)
    
    def add_question(
        self,
        session_id: str,
        question_id: int,
        question_text: str,
        category: str,
        difficulty: str
    ) -> bool:
        """Record a question being asked."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        question_memory = QuestionMemory(
            question_id=question_id,
            question_text=question_text,
            category=category,
            difficulty=difficulty
        )
        
        session.questions.append(question_memory)
        session.questions_asked += 1
        
        # Update topic analysis
        if category not in session.topic_analysis:
            session.topic_analysis[category] = TopicAnalysis(topic=category)
        
        session.topic_analysis[category].questions_asked += 1
        session.topic_analysis[category].questions.append(question_id)
        
        logger.info(f"Question {question_id} asked in session {session_id}")
        return True
    
    def add_answer(
        self,
        session_id: str,
        question_id: int,
        answer: str,
        score: float,
        evaluation: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record an answer and its evaluation."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Find the question
        question_memory = None
        for q in session.questions:
            if q.question_id == question_id:
                question_memory = q
                break
        
        if not question_memory:
            logger.warning(f"Question {question_id} not found in session {session_id}")
            return False
        
        # Update question with answer
        question_memory.answer = answer
        question_memory.score = score
        
        # Extract strengths and weaknesses from evaluation
        if evaluation:
            question_memory.strengths = evaluation.get('strengths', [])
            question_memory.weaknesses = evaluation.get('weaknesses', [])
        
        # Update totals
        session.total_score += score
        
        # Update topic analysis
        category = question_memory.category
        if category in session.topic_analysis:
            topic = session.topic_analysis[category]
            topic.total_score += score
            
            if score >= 7.0:
                topic.strong_count += 1
            elif score < 6.0:
                topic.weak_count += 1
        
        # Adjust difficulty
        self._adjust_difficulty(session)
        
        logger.info(f"Answer recorded for question {question_id}, score: {score}")
        return True
    
    def add_followup(
        self,
        session_id: str,
        question_id: int,
        followup_question: str,
        answer: Optional[str] = None,
        score: Optional[float] = None
    ) -> bool:
        """Record a follow-up question and answer."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Find the question
        for q in session.questions:
            if q.question_id == question_id:
                q.followup_asked = True
                q.followup_question = followup_question
                q.followup_answer = answer
                q.followup_score = score
                
                if answer and score is not None:
                    session.total_score += score
                    session.questions_asked += 1
                
                logger.info(f"Follow-up added for question {question_id}")
                return True
        
        return False
    
    def _adjust_difficulty(self, session: InterviewMemory):
        """Adjust question difficulty based on recent performance."""
        if session.questions_asked < 3:
            return  # Need at least 3 questions to adjust
        
        # Get last 3 scores
        recent_scores = [q.score for q in session.questions[-3:] if q.score is not None]
        
        if not recent_scores:
            return
        
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        # Adjust difficulty
        if avg_recent >= 8.0 and session.current_difficulty != 'hard':
            session.current_difficulty = 'hard'
            logger.info(f"Session {session.session_id}: Increasing difficulty to hard")
        elif avg_recent >= 6.5 and session.current_difficulty == 'easy':
            session.current_difficulty = 'medium'
            logger.info(f"Session {session.session_id}: Increasing difficulty to medium")
        elif avg_recent < 5.0 and session.current_difficulty != 'easy':
            session.current_difficulty = 'easy'
            logger.info(f"Session {session.session_id}: Decreasing difficulty to easy")
        elif avg_recent < 4.0 and session.current_difficulty == 'easy':
            # Consider providing more support
            logger.info(f"Session {session.session_id}: Candidate may need encouragement")
    
    def get_asked_questions(self, session_id: str) -> List[int]:
        """Get list of question IDs that have been asked."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        asked = [q.question_id for q in session.questions]
        
        # Include follow-ups
        for q in session.questions:
            if q.followup_asked:
                asked.append(q.question_id + 1000)  # Distinguish follow-ups
        
        return asked
    
    def get_question_texts(self, session_id: str) -> List[str]:
        """Get all question texts for context."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        texts = []
        for q in session.questions:
            texts.append(q.question_text)
            if q.followup_question:
                texts.append(q.followup_question)
        
        return texts
    
    def get_topic_scores(self, session_id: str) -> Dict[str, Dict[str, Any]]:
        """Get performance scores by topic."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            topic: {
                'average_score': analysis.average_score,
                'questions_asked': analysis.questions_asked,
                'status': analysis.performance_status,
                'strong_count': analysis.strong_count,
                'weak_count': analysis.weak_count
            }
            for topic, analysis in session.topic_analysis.items()
        }
    
    def complete_session(self, session_id: str) -> Optional[InterviewMemory]:
        """Mark session as completed."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        session.status = "completed"
        session.completed_at = datetime.now().isoformat()
        
        # Move to history (or keep in active for retrieval)
        logger.info(f"Session {session_id} completed. Final score: {session.average_score}")
        
        return session
    
    def pause_session(self, session_id: str) -> bool:
        """Pause an interview session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.status = "paused"
        logger.info(f"Session {session_id} paused")
        return True
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.status = "in_progress"
        logger.info(f"Session {session_id} resumed")
        return True
    
    def get_user_sessions(self, user_id: int) -> List[InterviewMemory]:
        """Get all sessions for a user."""
        session_ids = self.session_history.get(user_id, [])
        return [
            self.active_sessions[sid]
            for sid in session_ids
            if sid in self.active_sessions
        ]
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of conversation context for AI prompts."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        # Build summary
        summary = {
            'session_id': session_id,
            'company_mode': session.company_mode,
            'target_role': session.target_role,
            'questions_asked': session.questions_asked,
            'average_score': session.average_score,
            'current_difficulty': session.current_difficulty,
            'strong_topics': session.strong_topics,
            'weak_topics': session.weak_topics,
            'recent_questions': [],
            'needs_encouragement': session.average_score < 5.0 if session.questions_asked > 0 else False
        }
        
        # Add recent questions for context
        for q in session.questions[-3:]:
            summary['recent_questions'].append({
                'question': q.question_text,
                'category': q.category,
                'score': q.score,
                'was_difficult': q.score < 6.0 if q.score else None
            })
        
        return summary
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session from memory."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Session {session_id} cleared from memory")
            return True
        return False
    
    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for storage."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return session.to_dict()
    
    def import_session(self, session_data: Dict[str, Any]) -> InterviewMemory:
        """Import session data from storage."""
        session_id = session_data['session_id']
        
        # Reconstruct questions
        questions = [
            QuestionMemory(**q_data)
            for q_data in session_data.get('questions', [])
        ]
        
        # Reconstruct topic analysis
        topic_analysis = {
            k: TopicAnalysis(**v_data)
            for k, v_data in session_data.get('topic_analysis', {}).items()
        }
        
        # Create session
        memory = InterviewMemory(
            session_id=session_id,
            user_id=session_data['user_id'],
            resume_data=session_data['resume_data'],
            company_mode=session_data['company_mode'],
            target_role=session_data['target_role'],
            questions=questions,
            topic_analysis=topic_analysis,
            current_difficulty=session_data.get('current_difficulty', 'medium'),
            questions_asked=session_data.get('questions_asked', 0),
            total_score=session_data.get('total_score', 0.0),
            started_at=session_data.get('started_at'),
            completed_at=session_data.get('completed_at'),
            status=session_data.get('status', 'completed')
        )
        
        self.active_sessions[session_id] = memory
        return memory


# Global memory manager instance
memory_manager = InterviewMemoryManager()


def get_memory_manager() -> InterviewMemoryManager:
    """Get the global memory manager instance."""
    return memory_manager


def create_interview_memory(
    session_id: str,
    user_id: int,
    resume_data: Dict[str, Any],
    company_mode: str
) -> InterviewMemory:
    """Convenience function to create interview memory."""
    return memory_manager.create_session(session_id, user_id, resume_data, company_mode)
