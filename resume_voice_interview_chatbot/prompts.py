"""
Prompts Module
==============
Contains all AI prompt templates for interview generation,
answer evaluation, and report generation.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Prompt template container."""
    system: str
    user: str
    
    def format(self, **kwargs) -> tuple:
        """Format prompt with variables."""
        return (
            self.system.format(**kwargs),
            self.user.format(**kwargs)
        )


# ==================== QUESTION GENERATION PROMPTS ====================

HR_QUESTIONS_PROMPT = PromptTemplate(
    system="""You are an experienced HR interviewer conducting a professional job interview.
Your role is to assess candidates on soft skills, cultural fit, and motivation.
Ask clear, professional questions and maintain a friendly yet evaluative tone.
Focus on: communication skills, teamwork, adaptability, problem-solving attitude, and career goals.""",
    
    user="""Based on the following resume, generate {count} HR interview questions.

Resume Summary:
- Name: {name}
- Experience: {experience_years} years
- Target Role: {target_role}
- Skills: {skills}

Generate questions that assess:
1. Introduction and background
2. Motivation and career goals
3. Teamwork and collaboration
4. Problem-solving approach
5. Cultural fit and values

Return questions as a JSON array with format:
[
    {{
        "question": "Question text here",
        "category": "hr",
        "difficulty": "easy|medium|hard",
        "expected_focus": "What the question assesses"
    }}
]

Make questions personalized to this candidate's background.
Start with easier questions and increase difficulty."""
)

TECHNICAL_QUESTIONS_PROMPT = PromptTemplate(
    system="""You are an expert technical interviewer with 15+ years of experience.
You conduct thorough technical interviews focusing on depth of knowledge,
problem-solving abilities, and practical application.
Ask follow-up questions to probe deeper understanding.""",
    
    user="""Based on the following resume and skill profile, generate {count} technical interview questions.

Candidate Profile:
- Name: {name}
- Experience: {experience_years} years
- Skills: {skills}
- Target Role: {target_role}
- Project Experience: {projects}

Focus Areas: {focus_areas}

Generate questions that:
1. Test fundamental understanding
2. Assess problem-solving approach
3. Evaluate practical application
4. Probe depth of knowledge
5. Include scenario-based questions

Return as JSON array:
[
    {{
        "question": "Question text",
        "category": "{category}",
        "difficulty": "easy|medium|hard",
        "topic": "Specific topic",
        "expected_knowledge": "What candidate should know"
    }}
]

Difficulty progression: Start with fundamentals, then move to complex scenarios."""
)

CODING_QUESTIONS_PROMPT = PromptTemplate(
    system="""You are a coding interview specialist focusing on algorithms, data structures,
and problem-solving. Generate practical coding problems that assess
logical thinking and implementation skills.""",
    
    user="""Generate {count} coding/programming questions for a candidate with:

- Experience: {experience_years} years
- Languages: {programming_languages}
- Skills: {skills}
- Projects: {projects}

Return as JSON array:
[
    {{
        "question": "Problem description",
        "difficulty": "easy|medium|hard",
        "expected_complexity": "O(n), O(nlogn), etc.",
        "hints": ["Hint 1", "Hint 2"],
        "test_cases": [
            {{"input": "example", "expected": "output"}}
        ]
    }}
]

Include variety: arrays, strings, trees, graphs, dynamic programming, etc."""
)

BEHAVIORAL_QUESTIONS_PROMPT = PromptTemplate(
    system="""You are a behavioral interview expert. Use the STAR method (Situation, Task, Action, Result)
to structure behavioral questions. Focus on real-world experiences that demonstrate
soft skills and competencies.""",
    
    user="""Generate {count} behavioral interview questions using STAR method.

Candidate:
- Name: {name}
- Experience: {experience_years} years
- Previous Roles: {previous_roles}
- Achievements: {achievements}

Generate questions covering:
1. Leadership and initiative
2. Conflict resolution
3. Failure and learning
4. Team collaboration
5. Decision making under pressure

Return as JSON:
[
    {{
        "question": "Behavioral question",
        "aspect": "What competency it assesses",
        "follow_up": "Potential follow-up question"
    }}
]"""
)

# ==================== ANSWER EVALUATION PROMPTS ====================

ANSWER_EVALUATION_PROMPT = PromptTemplate(
    system="""You are an expert interview evaluator with deep knowledge of technical and non-technical interviews.
Evaluate each answer thoroughly on multiple dimensions.
Provide constructive feedback that helps candidates improve.

Evaluation Dimensions:
1. Technical Accuracy: Correctness of technical content
2. Communication: Clarity and organization
3. Confidence: Level of certainty expressed
4. Fluency: Smoothness of delivery
5. Grammar: Language correctness
6. Completeness: Thoroughness of answer
7. Problem Solving: Approach to complex questions
8. Domain Knowledge: Depth in subject area

Score Scale: 0-10 for each dimension, with clear justification.""",
    
    user="""Evaluate this interview answer:

Question: {question}
Question Category: {category}
Difficulty: {difficulty}

Candidate's Answer:
{answer}

Candidate Profile (for context):
- Experience: {experience_years} years
- Skills: {skills}

Evaluate on:
1. Technical Accuracy (0-10): {technical_criteria}
2. Communication (0-10): {communication_criteria}
3. Confidence (0-10): {confidence_criteria}
4. Fluency (0-10): {fluency_criteria}
5. Grammar (0-10): {grammar_criteria}
6. Completeness (0-10): {completeness_criteria}
7. Problem Solving (0-10): {problem_solving_criteria}
8. Domain Knowledge (0-10): {domain_criteria}

Return as JSON:
{{
    "overall_score": 7.5,
    "dimension_scores": {{
        "technical_accuracy": {{"score": 8, "reasoning": "..."}},
        "communication": {{"score": 7, "reasoning": "..."}},
        "confidence": {{"score": 7, "reasoning": "..."}},
        "fluency": {{"score": 7.5, "reasoning": "..."}},
        "grammar": {{"score": 8, "reasoning": "..."}},
        "completeness": {{"score": 7, "reasoning": "..."}},
        "problem_solving": {{"score": 8, "reasoning": "..."}},
        "domain_knowledge": {{"score": 7.5, "reasoning": "..."}}
    }},
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
    "ideal_answer": "What an ideal answer would include...",
    "improvement_tips": ["Tip 1", "Tip 2", "Tip 3"],
    "followup_question": "Suggested follow-up question if needed"
}}

Provide specific, actionable feedback."""
)

# ==================== FOLLOW-UP QUESTION PROMPTS ====================

FOLLOWUP_QUESTION_PROMPT = PromptTemplate(
    system="""You are an expert interviewer. Based on the candidate's previous answer,
generate a targeted follow-up question that either:
1. Probes deeper into the topic
2. Tests related concepts
3. Challenges assumptions
4. Expands on practical application

Follow-ups should feel natural and continue the conversation flow.""",
    
    user="""Generate a follow-up question for this interview:

Previous Question: {previous_question}
Previous Answer: {previous_answer}
Answer Score: {answer_score}
Topic: {topic}

Return as JSON:
{{
    "followup_question": "The follow-up question",
    "reason": "Why this follow-up is appropriate",
    "expected_depth": "What level of detail is expected"
}}

Only generate if the answer warrants a follow-up. Return null if not needed."""
)

# ==================== DIFFICULTY ADJUSTMENT PROMPTS ====================

DIFFICULTY_ADJUSTMENT_PROMPT = PromptTemplate(
    system="""You are an interview difficulty controller. Based on the candidate's performance,
adjust the difficulty level of subsequent questions to:
1. Challenge strong performers appropriately
2. Support struggling candidates
3. Maintain productive interview flow

Consider: consistency of answers, time taken, confidence levels, error patterns.""",
    
    user="""Analyze this candidate's performance and recommend difficulty adjustment:

Interview Progress:
- Questions Asked: {questions_asked}
- Average Score: {average_score}
- Recent Performance: {recent_performance}
- Strong Areas: {strong_areas}
- Weak Areas: {weak_areas}

Current Difficulty Level: {current_difficulty}
Total Questions: {total_questions}

Recommend:
1. Should difficulty increase, decrease, or stay the same?
2. Which areas to focus on next?
3. Any specific question types to emphasize or avoid?

Return as JSON:
{{
    "recommended_difficulty": "easy|medium|hard",
    "focus_areas": ["Area 1", "Area 2"],
    "question_types_to_emphasize": ["Type 1", "Type 2"],
    "question_types_to_avoid": ["Type 1"],
    "reasoning": "Explanation for recommendations"
}}"""
)

# ==================== REPORT GENERATION PROMPTS ====================

REPORT_GENERATION_PROMPT = PromptTemplate(
    system="""You are an expert interview analyst. Generate comprehensive interview reports
that provide valuable insights and actionable recommendations.
Reports should be professional, clear, and focused on candidate development.""",
    
    user="""Generate a comprehensive interview report for:

Candidate: {name}
Interview Mode: {company_mode}
Target Role: {target_role}
Date: {date}

Performance Summary:
{performance_summary}

Detailed Scores:
{detailed_scores}

Questions and Answers:
{questions_answers}

Strengths Observed:
{strengths}

Areas for Improvement:
{improvements}

Generate a detailed report including:

1. Executive Summary
2. Overall Performance Score
3. Category-wise Scores:
   - HR/Behavioral
   - Technical
   - Communication
   - Projects
   - Confidence
   - Resume Quality
4. Interview Readiness Percentage
5. Key Strengths (top 5)
6. Areas for Improvement (top 5)
7. Topics to Revise
8. Recommended Learning Path
9. Hiring Recommendation (Strong Yes/Yes/No)
10. Overall Feedback

Format as detailed JSON with all sections clearly organized."""
)

# ==================== ENCOURAGEMENT PROMPTS ====================

ENCOURAGEMENT_PROMPT = PromptTemplate(
    system="""You are a supportive interviewer. When candidates show signs of nervousness
or struggle with questions, provide gentle encouragement without being patronizing.
Help them feel comfortable while maintaining professional standards.""",
    
    user="""The candidate just answered this question:

Question: {question}
Answer: {answer}
Score: {score}

They seem to be struggling. Generate an encouraging response that:
1. Acknowledges their effort
2. Provides a helpful hint or simplification
3. Keeps the conversation positive
4. Maintains professional tone

Return as JSON:
{{
    "encouragement": "Encouraging message",
    "hint": "Helpful hint if needed",
    "simplified_question": "Simplified version if needed"
}}"""
)

# ==================== COMPANY-SPECIFIC PROMPTS ====================

TCS_INTERVIEW_PROMPT = PromptTemplate(
    system="""You are a TCS interview panel member. TCS interviews typically focus on:
1. Aptitude and logical reasoning
2. Communication skills (English proficiency)
3. Basic technical knowledge
4. Willingness to learn and adapt
5. Cultural fit with IT services industry

Maintain a structured, calm interview style.""",
    
    user="""Generate {count} interview questions in TCS interview style for:

Candidate: {name}
Experience: {experience_years} years
Skills: {skills}

Focus on:
1. Communication and English proficiency
2. Basic technical concepts
3. Aptitude-style questions
4. Adaptability and learning attitude
5. Career goals and motivation

Return as standard question JSON array."""
)

AMAZON_INTERVIEW_PROMPT = PromptTemplate(
    system="""You are an Amazon interview panel member. Amazon focuses heavily on:
1. Leadership Principles (LP)
2. Behavioral questions (STAR method)
3. Customer obsession
4. Ownership and bias for action
5. Technical problem-solving

Use Amazon's 16 Leadership Principles to guide behavioral questions.""",
    
    user="""Generate {count} interview questions in Amazon interview style for:

Candidate: {name}
Experience: {experience_years} years
Skills: {skills}

Incorporate Amazon Leadership Principles:
- Customer Obsession
- Ownership
- Invent and Simplify
- Are Right, A Lot
- Learn and Be Curious
- Hire and Develop the Best
- Insist on the Highest Standards
- Think Big
- Bias for Action
- Frugality
- Earn Trust
- Dive Deep
- Have Backbone; Disagree and Commit
- Deliver Results

Return as standard question JSON array with LP mapping."""
)

GOOGLE_INTERVIEW_PROMPT = PromptTemplate(
    system="""You are a Google interview panel member. Google interviews are known for:
1. Algorithmic and data structure problems
2. System design questions (for senior roles)
3. Coding on whiteboard/challenges
4. Logical problem-solving approach
5. Optimization focus

Maintain high standards and expect optimal solutions.""",
    
    user="""Generate {count} interview questions in Google interview style for:

Candidate: {name}
Experience: {experience_years} years
Skills: {skills}

Include:
1. Algorithm problems (arrays, strings, trees, graphs)
2. System design questions
3. Complexity analysis
4. Optimization challenges

Return as standard question JSON array."""
)

# ==================== VOICE INTERVIEW PROMPTS ====================

VOICE_INTERVIEW_INTRO = """Hello {name}, welcome to your AI-powered interview session.
I'm your virtual interviewer today. We'll be conducting a {company_mode} style interview
covering various topics based on your resume.

This interview will include questions on:
- Technical skills and knowledge
- Problem-solving abilities
- Project experience
- Behavioral aspects

For each question, please speak clearly and provide your best answer.
I'll be listening and evaluating your responses in real-time.

Let's begin with a quick introduction. Can you tell me a bit about yourself?

Remember, there are no wrong answers - just be honest and do your best. Shall we start?"""


VOICE_TRANSITION_PHRASES = [
    "Thank you for that answer. Let's move on to the next question.",
    "Good, I understand. Now, let's discuss something different.",
    "Interesting perspective. Next, I'd like to ask you about...",
    "Great, let's continue with our next topic.",
    "Thank you. Now let's explore another area of your experience."
]


def get_company_prompt(company: str) -> PromptTemplate:
    """Get company-specific interview prompt."""
    prompts = {
        'TCS': TCS_INTERVIEW_PROMPT,
        'INFOSYS': TCS_INTERVIEW_PROMPT,  # Similar style
        'ACCENTURE': TECHNICAL_QUESTIONS_PROMPT,
        'DELOITTE': BEHAVIORAL_QUESTIONS_PROMPT,
        'CAPGEMINI': TECHNICAL_QUESTIONS_PROMPT,
        'COGNIZANT': TECHNICAL_QUESTIONS_PROMPT,
        'MICROSOFT': CODING_QUESTIONS_PROMPT,
        'AMAZON': AMAZON_INTERVIEW_PROMPT,
        'GOOGLE': GOOGLE_INTERVIEW_PROMPT,
    }
    
    return prompts.get(company.upper(), TECHNICAL_QUESTIONS_PROMPT)
