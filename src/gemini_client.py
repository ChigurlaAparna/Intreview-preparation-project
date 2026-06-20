"""
Gemini API Client for Interview Prep
"""

import os
import json
from typing import Optional, Dict, List, Any


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY', '')
        self.model = None
        if self.api_key:
            self._initialize()
    
    def _initialize(self):
        """Initialize the Gemini model"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            # Use gemini-1.5-flash which is fast, capable, and widely available
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except ImportError:
            print("Please install google-generativeai: pip install google-generativeai")
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
    
    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return bool(self.api_key and self.model)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from Gemini"""
        if not self.is_configured():
            return "Gemini API not configured. Please provide a valid API key."
        
        try:
            generation_config = {
                'temperature': kwargs.get('temperature', 0.7),
                'max_output_tokens': kwargs.get('max_tokens', 2048),
            }
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def evaluate_answer(self, question: str, answer: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Evaluate an interview answer"""
        prompt = self._build_evaluation_prompt(question, answer, context)
        response = self.generate_response(prompt)
        
        return {
            'feedback': response,
            'question': question,
            'answer': answer
        }
    
    def _build_evaluation_prompt(self, question: str, answer: str, context: Optional[Dict]) -> str:
        """Build prompt for answer evaluation"""
        prompt = f"""You are an expert interview coach and technical interviewer.

EVALUATE THIS INTERVIEW RESPONSE:

Interview Question: {question}

Candidate's Answer: {answer}

Provide a comprehensive evaluation including:
1. Overall Score (1-10)
2. Strengths in the response
3. Areas for improvement
4. Suggested structure for a better answer
5. Example of an ideal response

Be specific, constructive, and encouraging."""
        return prompt
    
    def generate_technical_question(self, topic: str, difficulty: str = "medium") -> str:
        """Generate a technical interview question"""
        prompt = f"""Generate a {difficulty} difficulty technical interview question about {topic}.

The question should:
- Be relevant for a real technical interview
- Test understanding of core concepts
- Be clear and well-defined
- Be answerable in 3-5 minutes

Just return the question, nothing else."""
        
        return self.generate_response(prompt)
    
    def generate_behavioral_question(self, category: Optional[str] = None) -> Dict[str, str]:
        """Generate a behavioral interview question"""
        category_hint = f"Focus on {category}" if category else "Any relevant category"
        
        prompt = f"""Generate a behavioral interview question {category_hint}.

Return in this format:
Category: [category name]
Question: [the question]

Use the STAR method context in mind. The question should ask about a real work experience."""
        
        response = self.generate_response(prompt)
        
        # Parse the response
        result = {'category': 'General', 'question': response}
        if 'Category:' in response:
            parts = response.split('Category:')
            if len(parts) > 1:
                cat_part = parts[1].split('\n')[0].strip()
                result['category'] = cat_part
                result['question'] = response.split('Question:')[1].strip() if 'Question:' in response else response
        
        return result
    
    def analyze_resume(self, resume_text: str, job_description: Optional[str] = None) -> str:
        """Analyze a resume and provide feedback"""
        job_context = f"\n\nJob Description:\n{job_description}" if job_description else ""
        
        prompt = f"""You are an expert resume reviewer and career consultant.

Analyze this resume:{job_context}

Resume Content:
{resume_text}

Provide:
1. Overall Assessment (score 1-10)
2. Strengths
3. Areas for Improvement
4. ATS (Applicant Tracking System) Optimization Tips
5. Specific Suggestions

Be detailed and actionable in your feedback."""
        
        return self.generate_response(prompt)
    
    def suggest_improvements(self, current_answer: str, question_type: str) -> List[str]:
        """Suggest improvements for an interview answer"""
        prompt = f"""Given this {question_type} interview answer:

{current_answer}

Provide 5 specific, actionable suggestions to improve this answer. 
Format each suggestion as a numbered point starting with an action verb."""
        
        response = self.generate_response(prompt)
        suggestions = [line.strip() for line in response.split('\n') if line.strip()]
        return suggestions[:5]
