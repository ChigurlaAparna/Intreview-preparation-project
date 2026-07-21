"""
Answer Evaluator Module
=======================
Evaluates interview answers using AI on multiple dimensions
including technical accuracy, communication, and domain knowledge.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger

import config
from prompts import ANSWER_EVALUATION_PROMPT


@dataclass
class EvaluationScores:
    """Scores for each evaluation dimension."""
    technical_accuracy: float
    communication: float
    confidence: float
    fluency: float
    grammar: float
    completeness: float
    problem_solving: float
    domain_knowledge: float
    
    @property
    def overall(self) -> float:
        """Calculate weighted overall score."""
        weights = {
            'technical_accuracy': 0.20,
            'communication': 0.15,
            'confidence': 0.10,
            'fluency': 0.10,
            'grammar': 0.10,
            'completeness': 0.15,
            'problem_solving': 0.10,
            'domain_knowledge': 0.10
        }
        
        total = (
            self.technical_accuracy * weights['technical_accuracy'] +
            self.communication * weights['communication'] +
            self.confidence * weights['confidence'] +
            self.fluency * weights['fluency'] +
            self.grammar * weights['grammar'] +
            self.completeness * weights['completeness'] +
            self.problem_solving * weights['problem_solving'] +
            self.domain_knowledge * weights['domain_knowledge']
        )
        
        return round(total, 2)


@dataclass
class EvaluationResult:
    """Complete evaluation result."""
    overall_score: float
    dimension_scores: Dict[str, Dict[str, Any]]
    strengths: List[str]
    weaknesses: List[str]
    ideal_answer: str
    improvement_tips: List[str]
    followup_question: Optional[str]
    category_scores: Dict[str, float]  # HR, Technical, Communication, etc.


class AnswerEvaluator:
    """Evaluates interview answers using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize answer evaluator."""
        self.api_key = api_key or config.gemini_config.api_key
        self.ai_model = None
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
                        'temperature': 0.3,  # Lower temp for evaluation
                        'max_output_tokens': 2048
                    }
                )
                logger.info("Gemini AI initialized for answer evaluation")
        except ImportError:
            logger.warning("Google Generative AI not installed, using rule-based evaluation")
        except Exception as e:
            logger.error(f"Failed to initialize AI: {e}")
    
    def evaluate(
        self,
        question: Dict[str, Any],
        answer: str,
        resume_data: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate a single answer.
        
        Args:
            question: Question details
            answer: Candidate's answer
            resume_data: Optional resume data for context
            
        Returns:
            EvaluationResult with scores and feedback
        """
        logger.info(f"Evaluating answer for question: {question.get('question_text', '')[:50]}...")
        
        if not answer or len(answer.strip()) < 5:
            return self._empty_evaluation()
        
        if self.ai_model:
            try:
                return self._ai_evaluate(question, answer, resume_data)
            except Exception as e:
                logger.error(f"AI evaluation failed: {e}")
        
        return self._rule_based_evaluate(question, answer)
    
    def _ai_evaluate(
        self,
        question: Dict[str, Any],
        answer: str,
        resume_data: Optional[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate using AI."""
        # Prepare context
        skills = resume_data.get('extracted_skills', []) if resume_data else []
        experience_years = 0
        if resume_data:
            experience = resume_data.get('experience', [])
            experience_years = len(experience) * 2
        
        # Build evaluation prompt
        system_prompt = ANSWER_EVALUATION_PROMPT.system
        
        category_criteria = self._get_category_criteria(question.get('category', 'technical'))
        
        user_prompt = ANSWER_EVALUATION_PROMPT.user.format(
            question=question.get('question_text', ''),
            category=question.get('category', 'technical'),
            difficulty=question.get('difficulty', 'medium'),
            answer=answer,
            experience_years=experience_years,
            skills=', '.join(skills[:15]) if skills else 'Not specified',
            technical_criteria=category_criteria.get('technical', 'N/A'),
            communication_criteria='Clarity, structure, professional tone',
            confidence_criteria='Expresses certainty without being arrogant',
            fluency_criteria='Smooth delivery without long pauses',
            grammar_criteria='Correct sentence structure and word usage',
            completeness_criteria='Addresses all parts of the question',
            problem_solving_criteria='Logical approach to problem-solving',
            domain_criteria=category_criteria.get('domain', 'N/A')
        )
        
        try:
            response = self.ai_model.generate_content(user_prompt)
            response_text = response.text
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                data = json.loads(json_match.group())
                return self._parse_evaluation_result(data, question)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
        
        except Exception as e:
            logger.error(f"AI evaluation error: {e}")
        
        # Fallback to rule-based
        return self._rule_based_evaluate(question, answer)
    
    def _parse_evaluation_result(
        self,
        data: Dict[str, Any],
        question: Dict[str, Any]
    ) -> EvaluationResult:
        """Parse AI response into EvaluationResult."""
        dimension_scores = data.get('dimension_scores', {})
        
        # Ensure all dimensions exist
        default_dimension = {'score': 5.0, 'reasoning': 'Assessed by AI'}
        for dim in ['technical_accuracy', 'communication', 'confidence', 'fluency',
                   'grammar', 'completeness', 'problem_solving', 'domain_knowledge']:
            if dim not in dimension_scores:
                dimension_scores[dim] = default_dimension
        
        # Calculate overall from dimension scores
        scores = EvaluationScores(
            technical_accuracy=dimension_scores.get('technical_accuracy', {}).get('score', 5.0),
            communication=dimension_scores.get('communication', {}).get('score', 5.0),
            confidence=dimension_scores.get('confidence', {}).get('score', 5.0),
            fluency=dimension_scores.get('fluency', {}).get('score', 5.0),
            grammar=dimension_scores.get('grammar', {}).get('score', 5.0),
            completeness=dimension_scores.get('completeness', {}).get('score', 5.0),
            problem_solving=dimension_scores.get('problem_solving', {}).get('score', 5.0),
            domain_knowledge=dimension_scores.get('domain_knowledge', {}).get('score', 5.0)
        )
        
        # Calculate category score
        category = question.get('category', 'technical')
        category_scores = {
            'hr': 0, 'technical': 0, 'communication': 0,
            'project': 0, 'behavioral': 0, 'situational': 0
        }
        
        if category in category_scores:
            category_scores[category] = scores.overall
        
        return EvaluationResult(
            overall_score=data.get('overall_score', scores.overall),
            dimension_scores=dimension_scores,
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', []),
            ideal_answer=data.get('ideal_answer', ''),
            improvement_tips=data.get('improvement_tips', []),
            followup_question=data.get('followup_question'),
            category_scores=category_scores
        )
    
    def _rule_based_evaluate(
        self,
        question: Dict[str, Any],
        answer: str
    ) -> EvaluationResult:
        """Rule-based evaluation fallback."""
        category = question.get('category', 'technical')
        difficulty = question.get('difficulty', 'medium')
        
        # Base score adjustments
        base_score = 6.0 if difficulty == 'medium' else (5.0 if difficulty == 'hard' else 7.0)
        
        # Analyze answer characteristics
        answer_lower = answer.lower()
        word_count = len(answer.split())
        
        # Length scoring
        if word_count < 20:
            length_score = 4.0
        elif word_count < 50:
            length_score = 6.0
        elif word_count < 150:
            length_score = 8.0
        else:
            length_score = 7.0
        
        # Grammar heuristics
        grammar_issues = answer.count('  ')  # Double spaces
        grammar_score = max(3.0, 9.0 - grammar_issues)
        
        # Confidence heuristics (presence of hedging words)
        hedging_words = ['maybe', 'perhaps', 'i think', 'probably', 'might', 'could be']
        hedging_count = sum(1 for word in hedging_words if word in answer_lower)
        confidence_score = max(4.0, min(9.0, 8.0 - hedging_count * 0.5))
        
        # Technical keywords check
        category_keywords = self._get_category_keywords(category)
        keyword_matches = sum(1 for kw in category_keywords if kw in answer_lower)
        technical_score = min(9.0, 5.0 + keyword_matches * 0.5)
        
        # Communication (sentence structure)
        sentences = answer.split('.')
        avg_sentence_length = word_count / max(1, len(sentences))
        communication_score = 8.0 if 10 <= avg_sentence_length <= 25 else 6.0
        
        # Fluency (based on length and structure)
        if word_count < 30:
            fluency_score = 5.0
        else:
            fluency_score = 7.0
        
        # Completeness
        completeness_score = length_score * 0.9
        
        # Problem solving
        problem_solving_score = 6.0 if keyword_matches > 0 else 5.0
        
        # Domain knowledge
        domain_knowledge_score = technical_score * 0.9
        
        # Calculate overall
        scores = EvaluationScores(
            technical_accuracy=technical_score,
            communication=communication_score,
            confidence=confidence_score,
            fluency=fluency_score,
            grammar=grammar_score,
            completeness=completeness_score,
            problem_solving=problem_solving_score,
            domain_knowledge=domain_knowledge_score
        )
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if technical_score >= 7.0:
            strengths.append("Demonstrates good technical knowledge")
        elif technical_score < 5.0:
            weaknesses.append("Could strengthen technical depth")
        
        if communication_score >= 7.0:
            strengths.append("Clear and well-structured communication")
        else:
            weaknesses.append("Work on organizing your response")
        
        if confidence_score >= 7.0:
            strengths.append("Shows confidence in responses")
        else:
            weaknesses.append("Try to be more assertive")
        
        # Generate improvement tips
        improvement_tips = []
        if word_count < 50:
            improvement_tips.append("Provide more detailed examples")
        if grammar_score < 7.0:
            improvement_tips.append("Review grammar and sentence structure")
        if technical_score < 7.0:
            improvement_tips.append(f"Study {category} fundamentals more thoroughly")
        
        return EvaluationResult(
            overall_score=scores.overall,
            dimension_scores={
                'technical_accuracy': {'score': technical_score, 'reasoning': 'Keyword analysis'},
                'communication': {'score': communication_score, 'reasoning': 'Structure assessment'},
                'confidence': {'score': confidence_score, 'reasoning': 'Hedging word analysis'},
                'fluency': {'score': fluency_score, 'reasoning': 'Flow assessment'},
                'grammar': {'score': grammar_score, 'reasoning': 'Grammar check'},
                'completeness': {'score': completeness_score, 'reasoning': 'Length analysis'},
                'problem_solving': {'score': problem_solving_score, 'reasoning': 'Approach assessment'},
                'domain_knowledge': {'score': domain_knowledge_score, 'reasoning': 'Keyword matching'}
            },
            strengths=strengths if strengths else ["Shows effort in answering"],
            weaknesses=weaknesses if weaknesses else ["Room for improvement in detail"],
            ideal_answer=self._generate_ideal_answer(question, category),
            improvement_tips=improvement_tips if improvement_tips else ["Continue practicing"],
            followup_question=None,
            category_scores={'hr': scores.overall if category == 'hr' else 0,
                           'technical': scores.overall if category == 'technical' else 0}
        )
    
    def _empty_evaluation(self) -> EvaluationResult:
        """Return empty evaluation for no answer."""
        return EvaluationResult(
            overall_score=0.0,
            dimension_scores={
                'technical_accuracy': {'score': 0, 'reasoning': 'No answer provided'},
                'communication': {'score': 0, 'reasoning': 'No answer provided'},
                'confidence': {'score': 0, 'reasoning': 'No answer provided'},
                'fluency': {'score': 0, 'reasoning': 'No answer provided'},
                'grammar': {'score': 0, 'reasoning': 'No answer provided'},
                'completeness': {'score': 0, 'reasoning': 'No answer provided'},
                'problem_solving': {'score': 0, 'reasoning': 'No answer provided'},
                'domain_knowledge': {'score': 0, 'reasoning': 'No answer provided'}
            },
            strengths=[],
            weaknesses=["No answer provided"],
            ideal_answer="Please provide an answer to the question.",
            improvement_tips=["Try to answer each question"],
            followup_question=None,
            category_scores={}
        )
    
    def _get_category_criteria(self, category: str) -> Dict[str, str]:
        """Get evaluation criteria for category."""
        criteria = {
            'hr': {
                'technical': 'N/A for HR questions',
                'domain': 'Understanding of company culture and values'
            },
            'technical': {
                'technical': 'Correct technical concepts and accuracy',
                'domain': 'Depth of technical knowledge'
            },
            'programming': {
                'technical': 'Code correctness and efficiency',
                'domain': 'Algorithm and data structure knowledge'
            },
            'sql': {
                'technical': 'SQL syntax and query correctness',
                'domain': 'Database design and optimization knowledge'
            },
            'python': {
                'technical': 'Python syntax and best practices',
                'domain': 'Python ecosystem and libraries'
            },
            'machine_learning': {
                'technical': 'ML concepts and implementation',
                'domain': 'Machine learning algorithms and frameworks'
            },
            'behavioral': {
                'technical': 'N/A for behavioral questions',
                'domain': 'Soft skills and problem-solving approach'
            }
        }
        
        return criteria.get(category, {
            'technical': 'Correct and accurate response',
            'domain': 'Relevant domain knowledge'
        })
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Get relevant keywords for category."""
        keywords = {
            'hr': ['team', 'experience', 'leadership', 'challenge', 'success', 'learn'],
            'technical': ['algorithm', 'data', 'system', 'process', 'design', 'implement'],
            'programming': ['function', 'loop', 'variable', 'array', 'object', 'class'],
            'sql': ['select', 'join', 'table', 'query', 'database', 'index', 'primary'],
            'python': ['python', 'list', 'dictionary', 'function', 'module', 'package'],
            'machine_learning': ['model', 'training', 'data', 'algorithm', 'accuracy', 'prediction'],
            'projects': ['developed', 'created', 'implemented', 'designed', 'built', 'delivered'],
            'behavioral': ['situation', 'challenge', 'team', 'result', 'learned', 'approach']
        }
        
        return keywords.get(category, ['important', 'relevant', 'experience'])
    
    def _generate_ideal_answer(self, question: Dict[str, Any], category: str) -> str:
        """Generate ideal answer hint."""
        ideal_answers = {
            'hr': "A strong HR answer should include specific examples, demonstrate self-awareness, and show alignment with company values.",
            'technical': "A strong technical answer should explain the concept clearly, provide examples, and discuss related topics.",
            'programming': "A strong coding answer should explain the approach, discuss time/space complexity, and provide clean code.",
            'behavioral': "A strong behavioral answer should follow STAR format: describe the Situation, Task, Action, and Result.",
            'sql': "A strong SQL answer should include the correct query syntax and explain the logic behind it.",
            'python': "A strong Python answer should demonstrate understanding of Pythonic ways and best practices."
        }
        
        return ideal_answers.get(category, "A strong answer should be clear, concise, and demonstrate your knowledge.")
    
    def evaluate_batch(
        self,
        questions_answers: List[Dict[str, Any]],
        resume_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate multiple answers and calculate aggregate scores.
        
        Args:
            questions_answers: List of dicts with 'question' and 'answer' keys
            resume_data: Optional resume data for context
            
        Returns:
            Dictionary with aggregate evaluation results
        """
        evaluations = []
        total_score = 0
        
        for qa in questions_answers:
            eval_result = self.evaluate(
                qa.get('question', {}),
                qa.get('answer', ''),
                resume_data
            )
            evaluations.append(eval_result)
            total_score += eval_result.overall_score
        
        avg_score = total_score / len(evaluations) if evaluations else 0
        
        # Calculate category averages
        category_totals = {}
        category_counts = {}
        
        for eval_result in evaluations:
            for category, score in eval_result.category_scores.items():
                if score > 0:
                    category_totals[category] = category_totals.get(category, 0) + score
                    category_counts[category] = category_counts.get(category, 0) + 1
        
        category_scores = {
            cat: round(total / category_counts[cat], 2)
            for cat, total in category_totals.items()
        }
        
        # Collect all strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        
        for eval_result in evaluations:
            all_strengths.extend(eval_result.strengths)
            all_weaknesses.extend(eval_result.weaknesses)
        
        # Get unique items
        unique_strengths = list(dict.fromkeys(all_strengths))[:5]
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:5]
        
        return {
            'evaluations': [asdict(e) for e in evaluations],
            'average_score': round(avg_score, 2),
            'category_scores': category_scores,
            'top_strengths': unique_strengths,
            'top_weaknesses': unique_weaknesses,
            'total_questions': len(evaluations)
        }
    
    def to_dict(self, result: EvaluationResult) -> Dict[str, Any]:
        """Convert EvaluationResult to dictionary."""
        return asdict(result)


def evaluate_answer(
    question: Dict[str, Any],
    answer: str,
    resume_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function to evaluate an answer."""
    evaluator = AnswerEvaluator()
    result = evaluator.evaluate(question, answer, resume_data)
    return evaluator.to_dict(result)
