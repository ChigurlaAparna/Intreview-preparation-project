"""
Question Generator Module
========================
Generates personalized interview questions based on resume content,
target role, and company-specific interview styles.
"""

import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from loguru import logger

import config
from prompts import (
    HR_QUESTIONS_PROMPT,
    TECHNICAL_QUESTIONS_PROMPT,
    CODING_QUESTIONS_PROMPT,
    BEHAVIORAL_QUESTIONS_PROMPT,
    FOLLOWUP_QUESTION_PROMPT,
    DIFFICULTY_ADJUSTMENT_PROMPT,
    ENCOURAGEMENT_PROMPT,
    get_company_prompt
)


@dataclass
class InterviewQuestion:
    """Represents an interview question."""
    id: int
    question_number: int
    category: str
    question_text: str
    difficulty: str  # easy, medium, hard
    topic: Optional[str] = None
    expected_knowledge: Optional[str] = None
    hints: List[str] = field(default_factory=list)
    is_followup: bool = False
    parent_question_id: Optional[int] = None
    estimated_time: int = 120  # seconds


@dataclass
class QuestionBank:
    """Question bank for fallback/general questions."""
    
    # HR Questions
    HR_QUESTIONS = [
        {"question": "Tell me about yourself.", "difficulty": "easy", "topic": "introduction"},
        {"question": "What are your greatest strengths?", "difficulty": "easy", "topic": "self_assessment"},
        {"question": "What are your weaknesses?", "difficulty": "medium", "topic": "self_assessment"},
        {"question": "Why do you want to work here?", "difficulty": "medium", "topic": "motivation"},
        {"question": "Where do you see yourself in 5 years?", "difficulty": "medium", "topic": "career_goals"},
        {"question": "Why should we hire you?", "difficulty": "medium", "topic": "value_proposition"},
        {"question": "Tell me about a time you faced a challenge at work.", "difficulty": "medium", "topic": "problem_solving"},
        {"question": "How do you handle pressure and deadlines?", "difficulty": "medium", "topic": "stress_management"},
        {"question": "Describe your ideal work environment.", "difficulty": "easy", "topic": "work_preference"},
        {"question": "What motivates you?", "difficulty": "easy", "topic": "motivation"},
    ]
    
    # Technical Questions by category
    TECHNICAL_QUESTIONS = {
        "programming": [
            {"question": "What is the difference between list and tuple in Python?", "difficulty": "easy", "topic": "python_basics"},
            {"question": "Explain the difference between == and is in Python.", "difficulty": "easy", "topic": "python_basics"},
            {"question": "What is polymorphism in OOP?", "difficulty": "easy", "topic": "oop"},
            {"question": "Explain encapsulation and how it's achieved.", "difficulty": "easy", "topic": "oop"},
            {"question": "What is the difference between abstract class and interface?", "difficulty": "medium", "topic": "oop"},
            {"question": "What is inheritance and its types?", "difficulty": "easy", "topic": "oop"},
            {"question": "Explain the concept of recursion with an example.", "difficulty": "easy", "topic": "algorithms"},
            {"question": "What is the time complexity of binary search?", "difficulty": "easy", "topic": "algorithms"},
            {"question": "Explain the difference between stack and queue.", "difficulty": "easy", "topic": "data_structures"},
            {"question": "What is a hash table and how does it work?", "difficulty": "medium", "topic": "data_structures"},
        ],
        "sql": [
            {"question": "What is the difference between DELETE and TRUNCATE?", "difficulty": "easy", "topic": "sql_dml"},
            {"question": "Explain JOIN types with examples.", "difficulty": "medium", "topic": "sql_joins"},
            {"question": "What is normalization? Name its types.", "difficulty": "medium", "topic": "db_design"},
            {"question": "What is the difference between WHERE and HAVING?", "difficulty": "easy", "topic": "sql_filtering"},
            {"question": "Explain ACID properties.", "difficulty": "medium", "topic": "db_concepts"},
            {"question": "What is a primary key and foreign key?", "difficulty": "easy", "topic": "db_concepts"},
            {"question": "What are indexes and their types?", "difficulty": "medium", "topic": "db_optimization"},
            {"question": "Explain subqueries and their types.", "difficulty": "medium", "topic": "sql_advanced"},
        ],
        "python": [
            {"question": "What is PEP 8 and why is it important?", "difficulty": "easy", "topic": "python_best_practices"},
            {"question": "Explain list comprehension with examples.", "difficulty": "easy", "topic": "python_features"},
            {"question": "What is the difference between deep copy and shallow copy?", "difficulty": "medium", "topic": "python_concepts"},
            {"question": "What are Python decorators and how do they work?", "difficulty": "medium", "topic": "python_features"},
            {"question": "Explain the GIL (Global Interpreter Lock).", "difficulty": "hard", "topic": "python_internals"},
            {"question": "What is the difference between generators and iterators?", "difficulty": "medium", "topic": "python_features"},
            {"question": "Explain exception handling in Python.", "difficulty": "easy", "topic": "python_basics"},
            {"question": "What are *args and **kwargs?", "difficulty": "easy", "topic": "python_basics"},
        ],
        "machine_learning": [
            {"question": "What is the difference between supervised and unsupervised learning?", "difficulty": "easy", "topic": "ml_basics"},
            {"question": "Explain overfitting and how to prevent it.", "difficulty": "medium", "topic": "ml_concepts"},
            {"question": "What is regularization and why is it used?", "difficulty": "medium", "topic": "ml_techniques"},
            {"question": "Explain the bias-variance tradeoff.", "difficulty": "medium", "topic": "ml_concepts"},
            {"question": "What is cross-validation?", "difficulty": "easy", "topic": "ml_evaluation"},
            {"question": "Explain gradient descent.", "difficulty": "medium", "topic": "ml_optimization"},
            {"question": "What is the difference between precision and recall?", "difficulty": "easy", "topic": "ml_evaluation"},
            {"question": "What are the assumptions of linear regression?", "difficulty": "medium", "topic": "ml_models"},
        ],
        "deep_learning": [
            {"question": "What is a neural network?", "difficulty": "easy", "topic": "dl_basics"},
            {"question": "Explain forward propagation.", "difficulty": "easy", "topic": "dl_concepts"},
            {"question": "What is backpropagation?", "difficulty": "medium", "topic": "dl_training"},
            {"question": "What are activation functions? Name a few.", "difficulty": "easy", "topic": "dl_components"},
            {"question": "Explain CNN and its layers.", "difficulty": "medium", "topic": "dl_architectures"},
            {"question": "What is transfer learning?", "difficulty": "medium", "topic": "dl_techniques"},
            {"question": "What is the vanishing gradient problem?", "difficulty": "hard", "topic": "dl_problems"},
            {"question": "Explain LSTM and GRU.", "difficulty": "hard", "topic": "dl_architectures"},
        ],
        "nlp": [
            {"question": "What is tokenization?", "difficulty": "easy", "topic": "nlp_preprocessing"},
            {"question": "Explain stemming and lemmatization.", "difficulty": "easy", "topic": "nlp_preprocessing"},
            {"question": "What is TF-IDF?", "difficulty": "medium", "topic": "nlp_features"},
            {"question": "Explain word embeddings.", "difficulty": "medium", "topic": "nlp_embeddings"},
            {"question": "What are RNNs and their limitations?", "difficulty": "medium", "topic": "nlp_models"},
            {"question": "What is attention mechanism?", "difficulty": "hard", "topic": "nlp_techniques"},
            {"question": "Explain BERT and its applications.", "difficulty": "hard", "topic": "nlp_models"},
        ],
        "dbms": [
            {"question": "What is a database management system?", "difficulty": "easy", "topic": "db_basics"},
            {"question": "Explain the ACID properties.", "difficulty": "medium", "topic": "db_concepts"},
            {"question": "What is a transaction?", "difficulty": "easy", "topic": "db_concepts"},
            {"question": "Explain SQL vs NoSQL databases.", "difficulty": "easy", "topic": "db_types"},
            {"question": "What is database indexing?", "difficulty": "medium", "topic": "db_optimization"},
            {"question": "Explain CAP theorem.", "difficulty": "hard", "topic": "db_theory"},
        ],
        "operating_system": [
            {"question": "What is a process and thread?", "difficulty": "easy", "topic": "os_concepts"},
            {"question": "Explain deadlock and its conditions.", "difficulty": "medium", "topic": "os_concurrency"},
            {"question": "What is paging and segmentation?", "difficulty": "medium", "topic": "os_memory"},
            {"question": "Explain CPU scheduling algorithms.", "difficulty": "medium", "topic": "os_scheduling"},
            {"question": "What is virtual memory?", "difficulty": "easy", "topic": "os_memory"},
            {"question": "Explain race condition.", "difficulty": "medium", "topic": "os_concurrency"},
        ],
        "oop": [
            {"question": "What are the four pillars of OOP?", "difficulty": "easy", "topic": "oop_basics"},
            {"question": "Explain polymorphism with examples.", "difficulty": "easy", "topic": "oop"},
            {"question": "What is composition vs inheritance?", "difficulty": "medium", "topic": "oop_design"},
            {"question": "What is SOLID principles?", "difficulty": "hard", "topic": "oop_design"},
            {"question": "Explain encapsulation and abstraction.", "difficulty": "easy", "topic": "oop"},
        ],
        "projects": [
            {"question": "Tell me about your most challenging project.", "difficulty": "medium", "topic": "project_experience"},
            {"question": "What was your role in your team projects?", "difficulty": "easy", "topic": "teamwork"},
            {"question": "What technologies did you use in your projects?", "difficulty": "easy", "topic": "technical_skills"},
            {"question": "Describe a project where you solved a difficult problem.", "difficulty": "medium", "topic": "problem_solving"},
            {"question": "What would you do differently in your projects?", "difficulty": "medium", "topic": "reflection"},
        ]
    }
    
    # Behavioral Questions
    BEHAVIORAL_QUESTIONS = [
        {"question": "Tell me about a time you had a conflict with a coworker.", "difficulty": "medium", "topic": "conflict_resolution"},
        {"question": "Describe a situation where you had to meet a tight deadline.", "difficulty": "medium", "topic": "time_management"},
        {"question": "Give an example of when you showed leadership.", "difficulty": "medium", "topic": "leadership"},
        {"question": "Tell me about a time you failed and how you handled it.", "difficulty": "hard", "topic": "resilience"},
        {"question": "Describe a time you had to learn something quickly.", "difficulty": "easy", "topic": "learning_ability"},
        {"question": "Give an example of when you went above and beyond.", "difficulty": "medium", "topic": "initiative"},
        {"question": "Tell me about a time you received critical feedback.", "difficulty": "medium", "topic": "receptiveness"},
        {"question": "Describe a project you led from start to finish.", "difficulty": "medium", "topic": "ownership"},
    ]
    
    # Situational Questions
    SITUATIONAL_QUESTIONS = [
        {"question": "How would you handle a difficult stakeholder?", "difficulty": "medium", "topic": "stakeholder_management"},
        {"question": "What would you do if you disagreed with your manager?", "difficulty": "medium", "topic": "conflict_resolution"},
        {"question": "How would you prioritize multiple urgent tasks?", "difficulty": "medium", "topic": "prioritization"},
        {"question": "What would you do if you made a mistake that no one noticed?", "difficulty": "medium", "topic": "accountability"},
        {"question": "How would you handle a team member not pulling their weight?", "difficulty": "hard", "topic": "team_management"},
    ]


class QuestionGenerator:
    """Generates interview questions using AI and fallback question banks."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize question generator."""
        self.api_key = api_key or config.gemini_config.api_key
        self.ai_model = None
        self.question_bank = QuestionBank()
        self.generated_questions = []
        self._init_ai()
    
    def _init_ai(self):
        """Initialize AI model."""
        try:
            import google.generativeai as genai
            
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.ai_model = genai.GenerativeModel(
                    config.gemini_config.model,
                    generation_config={
                        'temperature': 0.8,
                        'max_output_tokens': 4096
                    }
                )
                logger.info("Gemini AI initialized for question generation")
        except ImportError:
            logger.warning("Google Generative AI not installed, using question bank")
        except Exception as e:
            logger.error(f"Failed to initialize AI: {e}")
    
    def generate_questions(
        self,
        resume_data: Dict[str, Any],
        company_mode: str,
        count: int = 15,
        categories: Optional[List[str]] = None
    ) -> List[InterviewQuestion]:
        """
        Generate interview questions based on resume and company mode.
        
        Args:
            resume_data: Parsed resume data
            company_mode: Target company (TCS, INFOSYS, AMAZON, etc.)
            count: Number of questions to generate
            categories: Specific categories to focus on
            
        Returns:
            List of InterviewQuestion objects
        """
        logger.info(f"Generating {count} questions for {company_mode} interview")
        
        questions = []
        question_id = 1
        
        # If AI is available, use it
        if self.ai_model:
            questions = self._generate_ai_questions(
                resume_data, company_mode, count, categories
            )
        else:
            # Use question bank
            questions = self._generate_bank_questions(
                resume_data, company_mode, count, categories
            )
        
        self.generated_questions = questions
        logger.info(f"Generated {len(questions)} questions")
        
        return questions
    
    def _generate_ai_questions(
        self,
        resume_data: Dict[str, Any],
        company_mode: str,
        count: int,
        categories: Optional[List[str]]
    ) -> List[InterviewQuestion]:
        """Generate questions using AI."""
        questions = []
        question_id = 1
        
        # Get company-specific prompt
        company_prompt = get_company_prompt(company_mode)
        
        # Prepare context
        personal_info = resume_data.get('personal_info', {})
        skills = resume_data.get('extracted_skills', [])
        experience = resume_data.get('experience', [])
        projects = resume_data.get('projects', [])
        education = resume_data.get('education', [])
        
        # Calculate experience years
        experience_years = self._calculate_experience_years(experience)
        
        # Prepare skills string
        skills_str = ', '.join(skills[:20]) if skills else 'Not specified'
        
        # Prepare projects string
        project_names = [p.get('name', '') for p in projects[:5]]
        projects_str = ', '.join([p for p in project_names if p]) if project_names else 'Not specified'
        
        # Previous roles
        previous_roles = [exp.get('title', '') for exp in experience[:3]]
        roles_str = ', '.join([r for r in previous_roles if r]) if previous_roles else 'Entry level'
        
        # Generate by category distribution
        category_distribution = self._get_category_distribution(company_mode)
        
        for category, percentage in category_distribution.items():
            if categories and category not in categories:
                continue
            
            category_count = max(1, int(count * percentage))
            
            # Build AI prompt
            if category == 'hr':
                system, user = HR_QUESTIONS_PROMPT.format(
                    count=category_count,
                    name=personal_info.get('name', 'Candidate'),
                    experience_years=experience_years,
                    target_role=resume_data.get('analysis', {}).get('target_role', 'Software Engineer'),
                    skills=skills_str
                )
            elif category in ['sql', 'python', 'machine_learning', 'deep_learning', 'nlp']:
                system, user = TECHNICAL_QUESTIONS_PROMPT.format(
                    count=category_count,
                    name=personal_info.get('name', 'Candidate'),
                    experience_years=experience_years,
                    skills=skills_str,
                    target_role=resume_data.get('analysis', {}).get('target_role', 'Software Engineer'),
                    projects=projects_str,
                    focus_areas=category,
                    category=category
                )
            elif category == 'programming':
                system, user = CODING_QUESTIONS_PROMPT.format(
                    count=category_count,
                    experience_years=experience_years,
                    programming_languages=skills_str,
                    skills=skills_str,
                    projects=projects_str
                )
            elif category == 'behavioral':
                achievements = resume_data.get('achievements', [])
                achievement_str = ', '.join([a.get('description', '') for a in achievements[:5]])
                system, user = BEHAVIORAL_QUESTIONS_PROMPT.format(
                    count=category_count,
                    name=personal_info.get('name', 'Candidate'),
                    experience_years=experience_years,
                    previous_roles=roles_str,
                    achievements=achievement_str or 'Not specified'
                )
            else:
                continue
            
            # Generate AI questions
            try:
                response = self.ai_model.generate_content(user)
                response_text = response.text
                
                # Parse JSON
                import re
                json_match = re.search(r'\[[\s\S]*\]', response_text)
                if json_match:
                    ai_questions = json.loads(json_match.group())
                    
                    for q in ai_questions:
                        difficulty = q.get('difficulty', 'medium')
                        difficulty_order = {'easy': 1, 'medium': 2, 'hard': 3}
                        order = difficulty_order.get(difficulty, 2)
                        
                        questions.append(InterviewQuestion(
                            id=question_id,
                            question_number=question_id,
                            category=category,
                            question_text=q.get('question', ''),
                            difficulty=difficulty,
                            topic=q.get('topic'),
                            expected_knowledge=q.get('expected_knowledge'),
                            hints=q.get('hints', []),
                            is_followup=False,
                            estimated_time=self._get_estimated_time(difficulty)
                        ))
                        question_id += 1
                        
            except Exception as e:
                logger.warning(f"AI question generation failed for {category}: {e}")
                # Fall back to question bank
                bank_questions = self._get_bank_questions(category, category_count)
                for q in bank_questions:
                    # Map 'question' to 'question_text'
                    questions.append(InterviewQuestion(
                        id=question_id,
                        question_number=question_id,
                        question_text=q.get('question', ''),
                        category=category,
                        difficulty=q.get('difficulty', 'medium'),
                        topic=q.get('topic')
                    ))
                    question_id += 1
        
        # Shuffle questions for variety
        random.shuffle(questions)
        
        # Re-number questions
        for i, q in enumerate(questions):
            q.question_number = i + 1
        
        return questions[:count]
    
    def _generate_bank_questions(
        self,
        resume_data: Dict[str, Any],
        company_mode: str,
        count: int,
        categories: Optional[List[str]]
    ) -> List[InterviewQuestion]:
        """Generate questions from question bank - personalized with resume data."""
        questions = []
        question_id = 1
        
        # Extract resume data for personalization
        personal_info = resume_data.get('personal_info', {})
        skills = resume_data.get('extracted_skills', [])
        experience = resume_data.get('experience', [])
        projects = resume_data.get('projects', [])
        education = resume_data.get('education', [])
        
        candidate_name = personal_info.get('name', 'the candidate')
        target_role = resume_data.get('analysis', {}).get('target_role', 'Software Engineer')
        
        # Get project names for project-based questions
        project_names = []
        project_tech = []
        for p in projects[:5]:
            name = p.get('name', '') or p.get('title', '')
            if name:
                project_names.append(name)
            tech = p.get('technologies', '') or p.get('tech_stack', '')
            if tech:
                project_tech.append(tech)
        
        # Get skills for technical questions
        skills_lower = [s.lower() for s in skills]
        has_python = any('python' in s for s in skills_lower)
        has_sql = any('sql' in s or 'database' in s for s in skills_lower)
        has_ml = any('machine learning' in s or 'ml' in s for s in skills_lower)
        has_java = any('java' in s for s in skills_lower)
        has_javascript = any('javascript' in s or 'js' in s for s in skills_lower)
        
        # Generate personalized HR questions
        hr_questions = self._generate_personalized_hr_questions(
            candidate_name, target_role, project_names, skills, count=3
        )
        for q_text in hr_questions:
            questions.append(InterviewQuestion(
                id=question_id, question_number=question_id,
                category='hr', question_text=q_text,
                difficulty='medium', topic='personal'
            ))
            question_id += 1
        
        # Generate personalized project questions
        if project_names:
            project_questions = self._generate_personalized_project_questions(
                project_names, project_tech, count=3
            )
            for q_text in project_questions:
                questions.append(InterviewQuestion(
                    id=question_id, question_number=question_id,
                    category='projects', question_text=q_text,
                    difficulty='medium', topic='project_details'
                ))
                question_id += 1
        
        # Generate personalized technical questions based on skills
        if has_python:
            questions.append(InterviewQuestion(
                id=question_id, question_number=question_id,
                category='python',
                question_text=f"Based on your Python experience, explain how you would handle data processing in a project. What Python libraries have you worked with?",
                difficulty='medium', topic='python'
            ))
            question_id += 1
        
        if has_ml:
            questions.append(InterviewQuestion(
                id=question_id, question_number=question_id,
                category='machine_learning',
                question_text=f"Tell me about your machine learning experience. What models have you trained and evaluated?",
                difficulty='medium', topic='ml'
            ))
            question_id += 1
        
        if has_sql:
            questions.append(InterviewQuestion(
                id=question_id, question_number=question_id,
                category='sql',
                question_text="How have you used SQL in your projects? Describe a complex query you wrote.",
                difficulty='medium', topic='sql'
            ))
            question_id += 1
        
        # Add experience-based questions
        if experience:
            latest_exp = experience[0] if experience else {}
            role = latest_exp.get('title', 'your role')
            questions.append(InterviewQuestion(
                id=question_id, question_number=question_id,
                category='technical',
                question_text=f"In your role as {role}, what was the most challenging technical problem you solved? How did you approach it?",
                difficulty='medium', topic='problem_solving'
            ))
            question_id += 1
        
        # Add coding questions
        coding_qs = self._get_bank_questions('programming', 2)
        for q in coding_qs:
            questions.append(InterviewQuestion(
                id=question_id, question_number=question_id,
                category='programming', question_text=q.get('question', ''),
                difficulty=q.get('difficulty', 'medium'), topic=q.get('topic')
            ))
            question_id += 1
        
        # Add behavioral questions
        behavioral_qs = self._get_bank_questions('behavioral', 2)
        for q in behavioral_qs:
            questions.append(InterviewQuestion(
                id=question_id, question_number=question_id,
                category='behavioral', question_text=q.get('question', ''),
                difficulty=q.get('difficulty', 'medium'), topic=q.get('topic')
            ))
            question_id += 1
        
        # Shuffle and limit
        random.shuffle(questions)
        questions = questions[:count]
        
        # Re-number
        for i, q in enumerate(questions):
            q.question_number = i + 1
        
        return questions
    
    def _generate_personalized_hr_questions(self, name: str, role: str, projects: List[str], skills: List[str], count: int = 3) -> List[str]:
        """Generate HR questions personalized to the candidate."""
        questions = [
            f"Hello {name}, could you briefly introduce yourself and tell us about your background as a {role}?",
            f"What motivated you to pursue a career as a {role}? What do you find most exciting about this field?",
            f"Looking at your projects including {projects[0] if projects else 'your work'}, what has been your greatest professional achievement so far?",
            f"Tell me about a time when you had to learn a new technology quickly. How did you approach it?",
            f"Why are you interested in joining our company, and what do you hope to contribute?",
            f"Where do you see yourself in the next 3-5 years, and how does this role align with your career goals?",
        ]
        return random.sample(questions, min(count, len(questions)))
    
    def _generate_personalized_project_questions(self, projects: List[str], tech: List[str], count: int = 3) -> List[str]:
        """Generate project questions personalized to the candidate's projects."""
        questions = []
        for i, proj in enumerate(projects[:3]):
            questions.append(f"Tell me about the project '{proj}'. What was your role and what challenges did you face?")
            if tech and i < len(tech):
                questions.append(f"In project '{proj}', you mentioned working with {tech[i]}. Can you explain what you built and how it works?")
        return questions[:count]
    
    def _get_bank_questions(self, category: str, count: int) -> List[Dict]:
        """Get questions from question bank."""
        if category == 'hr':
            return random.sample(self.question_bank.HR_QUESTIONS, min(count, len(self.question_bank.HR_QUESTIONS)))
        elif category == 'behavioral':
            return random.sample(self.question_bank.BEHAVIORAL_QUESTIONS, min(count, len(self.question_bank.BEHAVIORAL_QUESTIONS)))
        elif category == 'situational':
            return random.sample(self.question_bank.SITUATIONAL_QUESTIONS, min(count, len(self.question_bank.SITUATIONAL_QUESTIONS)))
        elif category in self.question_bank.TECHNICAL_QUESTIONS:
            tech_questions = self.question_bank.TECHNICAL_QUESTIONS.get(category, [])
            return random.sample(tech_questions, min(count, len(tech_questions)))
        else:
            return random.sample(self.question_bank.TECHNICAL_QUESTIONS['programming'], min(count, 5))
    
    def _get_category_distribution(self, company_mode: str) -> Dict[str, float]:
        """Get question category distribution for company."""
        distributions = {
            'TCS': {'hr': 0.30, 'technical': 0.25, 'programming': 0.15, 'projects': 0.15, 'behavioral': 0.15},
            'INFOSYS': {'hr': 0.25, 'technical': 0.30, 'programming': 0.20, 'projects': 0.15, 'behavioral': 0.10},
            'ACCENTURE': {'hr': 0.20, 'technical': 0.25, 'projects': 0.25, 'behavioral': 0.20, 'situational': 0.10},
            'DELOITTE': {'hr': 0.20, 'technical': 0.20, 'behavioral': 0.35, 'situational': 0.15, 'projects': 0.10},
            'CAPGEMINI': {'hr': 0.25, 'technical': 0.30, 'programming': 0.20, 'projects': 0.15, 'behavioral': 0.10},
            'COGNIZANT': {'hr': 0.25, 'technical': 0.30, 'programming': 0.15, 'projects': 0.15, 'behavioral': 0.15},
            'MICROSOFT': {'hr': 0.10, 'technical': 0.25, 'programming': 0.40, 'projects': 0.15, 'behavioral': 0.10},
            'AMAZON': {'hr': 0.15, 'technical': 0.25, 'programming': 0.30, 'behavioral': 0.25, 'situational': 0.05},
            'GOOGLE': {'hr': 0.05, 'technical': 0.20, 'programming': 0.50, 'projects': 0.15, 'behavioral': 0.10},
        }
        
        return distributions.get(company_mode.upper(), distributions['TCS'])
    
    def _calculate_experience_years(self, experience: List[Dict]) -> int:
        """Calculate total experience years."""
        # Simplified calculation
        return len(experience) * 2 if experience else 0
    
    def _get_estimated_time(self, difficulty: str) -> int:
        """Get estimated answer time based on difficulty."""
        times = {
            'easy': 60,
            'medium': 120,
            'hard': 180
        }
        return times.get(difficulty, 120)
    
    def generate_followup(
        self,
        previous_question: InterviewQuestion,
        previous_answer: str,
        answer_score: float
    ) -> Optional[InterviewQuestion]:
        """Generate a follow-up question based on previous answer."""
        if not self.ai_model:
            return None
        
        if answer_score < 7.0:  # Only follow up on weaker answers
            try:
                system, user = FOLLOWUP_QUESTION_PROMPT.format(
                    previous_question=previous_question.question_text,
                    previous_answer=previous_answer,
                    answer_score=answer_score,
                    topic=previous_question.topic or previous_question.category
                )
                
                response = self.ai_model.generate_content(user)
                response_text = response.text
                
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    data = json.loads(json_match.group())
                    followup_text = data.get('followup_question')
                    
                    if followup_text:
                        return InterviewQuestion(
                            id=len(self.generated_questions) + 1,
                            question_number=previous_question.question_number,
                            category=previous_question.category,
                            question_text=followup_text,
                            difficulty='medium',
                            topic=previous_question.topic,
                            is_followup=True,
                            parent_question_id=previous_question.id
                        )
                        
            except Exception as e:
                logger.warning(f"Follow-up generation failed: {e}")
        
        return None
    
    def get_encouragement(
        self,
        question: InterviewQuestion,
        answer: str,
        score: float
    ) -> Optional[str]:
        """Get encouraging message if candidate is struggling."""
        if not self.ai_model or score >= 6.0:
            return None
        
        try:
            system, user = ENCOURAGEMENT_PROMPT.format(
                question=question.question_text,
                answer=answer,
                score=score
            )
            
            response = self.ai_model.generate_content(user)
            response_text = response.text
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('encouragement')
                
        except Exception as e:
            logger.warning(f"Encouragement generation failed: {e}")
        
        return None
    
    def get_next_difficulty(
        self,
        questions_asked: int,
        scores: List[float],
        current_difficulty: str
    ) -> str:
        """Determine difficulty for next question."""
        if not questions_asked:
            return 'medium'
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 8.0:
            return 'hard'
        elif avg_score >= 6.0:
            return 'medium'
        else:
            return 'easy'


def generate_interview_questions(
    resume_data: Dict[str, Any],
    company_mode: str,
    count: int = 15,
    categories: Optional[List[str]] = None
) -> List[Dict]:
    """Convenience function to generate questions."""
    generator = QuestionGenerator()
    questions = generator.generate_questions(resume_data, company_mode, count, categories)
    return [asdict(q) for q in questions]
