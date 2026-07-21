"""
Resume Analyzer Module
=====================
Analyzes parsed resume data to provide insights on skills, gaps,
strengths, weaknesses, and recommendations using AI.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger

import config


# Industry-standard skills for different roles
INDUSTRY_SKILLS = {
    'software_engineer': {
        'required': [
            'python', 'java', 'javascript', 'git', 'sql',
            'data structures', 'algorithms', 'problem solving'
        ],
        'recommended': [
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'microservices', 'ci/cd', 'testing', 'agile'
        ],
        'nice_to_have': [
            'machine learning', 'blockchain', 'serverless', 'terraform'
        ]
    },
    'data_scientist': {
        'required': [
            'python', 'sql', 'machine learning', 'statistics',
            'pandas', 'numpy', 'data visualization'
        ],
        'recommended': [
            'deep learning', 'nlp', 'computer vision', 'tensorflow',
            'pytorch', 'scikit-learn', 'big data', 'spark'
        ],
        'nice_to_have': [
            'mlops', 'kubeflow', 'airflow', 'cloud ml platforms'
        ]
    },
    'full_stack_developer': {
        'required': [
            'javascript', 'html', 'css', 'react', 'node.js',
            'sql', 'git', 'rest api'
        ],
        'recommended': [
            'typescript', 'vue', 'angular', 'graphql', 'docker',
            'ci/cd', 'postgresql', 'mongodb'
        ],
        'nice_to_have': [
            'aws', 'gcp', 'serverless', 'web sockets'
        ]
    },
    'backend_developer': {
        'required': [
            'python', 'java', 'sql', 'git', 'api design',
            'data structures', 'algorithms'
        ],
        'recommended': [
            'microservices', 'docker', 'kubernetes', 'redis',
            'message queues', 'caching', 'testing'
        ],
        'nice_to_have': [
            'aws', 'terraform', 'elasticsearch', 'graph databases'
        ]
    },
    'ml_engineer': {
        'required': [
            'python', 'machine learning', 'deep learning', 'tensorflow',
            'pytorch', 'sql', 'git'
        ],
        'recommended': [
            'mlops', 'kubernetes', 'docker', 'aws sagemaker',
            'vertex ai', 'airflow', 'feature engineering'
        ],
        'nice_to_have': [
            ' reinforcement learning', 'computer vision', 'nlp', 'llm'
        ]
    },
    'devops_engineer': {
        'required': [
            'linux', 'docker', 'kubernetes', 'ci/cd', 'git',
            'scripting', 'aws', 'monitoring'
        ],
        'recommended': [
            'terraform', 'ansible', 'helm', 'prometheus',
            'grafana', 'vault', 'sonarqube'
        ],
        'nice_to_have': [
            'service mesh', 'chaos engineering', 'security scanning'
        ]
    }
}


@dataclass
class SkillGap:
    """Represents a skill gap."""
    skill: str
    priority: str  # 'required', 'recommended', 'nice_to_have'
    reason: str
    learning_resources: Optional[List[str]] = None


@dataclass
class ResumeStrength:
    """Represents a resume strength."""
    category: str
    description: str
    impact: str


@dataclass
class ResumeWeakness:
    """Represents a resume weakness."""
    category: str
    issue: str
    severity: str  # 'high', 'medium', 'low'
    suggestion: str


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    target_role: str
    skill_gaps: List[SkillGap]
    strengths: List[ResumeStrength]
    weaknesses: List[ResumeWeakness]
    overall_score: float
    readiness_percentage: float
    key_recommendations: List[str]
    learning_path: Dict[str, List[str]]


class ResumeAnalyzer:
    """Analyzes resumes and provides actionable insights."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize analyzer with AI capabilities."""
        self.api_key = api_key or config.gemini_config.api_key
        self.analysis_model = None
        self._init_ai()
    
    def _init_ai(self):
        """Initialize AI model for analysis."""
        try:
            import google.generativeai as genai
            
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.analysis_model = genai.GenerativeModel(
                    config.gemini_config.model,
                    generation_config={
                        'temperature': 0.3,  # Lower temp for analysis
                        'max_output_tokens': 2048
                    }
                )
                logger.info("Gemini AI initialized for resume analysis")
        except ImportError:
            logger.warning("Google Generative AI not installed, using rule-based analysis")
        except Exception as e:
            logger.error(f"Failed to initialize AI: {e}")
    
    def analyze(
        self,
        parsed_resume: Dict[str, Any],
        target_role: Optional[str] = None,
        target_companies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze resume and generate comprehensive report.
        
        Args:
            parsed_resume: Parsed resume data from ResumeParser
            target_role: Target job role (auto-detected if not provided)
            target_companies: List of target companies
            
        Returns:
            Analysis result dictionary
        """
        logger.info("Starting resume analysis")
        
        # Extract skills
        skills = parsed_resume.get('extracted_skills', [])
        if not skills and parsed_resume.get('skills'):
            skills = [s.get('name', '') for s in parsed_resume['skills']]
        
        # Detect target role if not provided
        if not target_role:
            target_role = self._detect_target_role(skills, parsed_resume)
        
        # Perform analysis
        skill_gaps = self._analyze_skill_gaps(skills, target_role)
        strengths = self._analyze_strengths(parsed_resume, skills, target_role)
        weaknesses = self._analyze_weaknesses(parsed_resume, skills, target_role)
        
        # Calculate scores
        overall_score = self._calculate_overall_score(parsed_resume, strengths, weaknesses)
        readiness = self._calculate_readiness_percentage(
            skill_gaps, weaknesses, parsed_resume
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            skill_gaps, weaknesses, parsed_resume
        )
        
        # Create learning path
        learning_path = self._create_learning_path(skill_gaps)
        
        # Try AI-enhanced analysis
        if self.analysis_model:
            try:
                ai_insights = self._get_ai_insights(parsed_resume, target_role)
                strengths.extend(ai_insights.get('additional_strengths', []))
                weaknesses.extend(ai_insights.get('additional_weaknesses', []))
                recommendations.extend(ai_insights.get('additional_recommendations', []))
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")
        
        # Compile result
        result = AnalysisResult(
            target_role=target_role,
            skill_gaps=skill_gaps,
            strengths=strengths,
            weaknesses=weaknesses,
            overall_score=overall_score,
            readiness_percentage=readiness,
            key_recommendations=recommendations[:10],  # Top 10
            learning_path=learning_path
        )
        
        logger.info(f"Analysis complete. Score: {overall_score}, Readiness: {readiness}%")
        
        return self._to_dict(result)
    
    def _detect_target_role(self, skills: List[str], parsed_resume: Dict) -> str:
        """Auto-detect target role based on skills."""
        skill_set = set(s.lower() for s in skills)
        
        # Check experience titles
        for exp in parsed_resume.get('experience', []):
            title = exp.get('title', '').lower()
            if any(kw in title for kw in ['data scientist', 'data science']):
                return 'data_scientist'
            if any(kw in title for kw in ['ml engineer', 'machine learning engineer']):
                return 'ml_engineer'
            if any(kw in title for kw in ['full stack', 'fullstack']):
                return 'full_stack_developer'
            if any(kw in title for kw in ['backend', 'back-end']):
                return 'backend_developer'
            if any(kw in title for kw in ['devops', 'sre', 'site reliability']):
                return 'devops_engineer'
            if any(kw in title for kw in ['software', 'developer', 'engineer']):
                return 'software_engineer'
        
        # Match based on skills
        scores = {}
        for role, role_skills in INDUSTRY_SKILLS.items():
            required_matches = len(skill_set & set(r.lower() for r in role_skills['required']))
            recommended_matches = len(skill_set & set(r.lower() for r in role_skills['recommended']))
            
            total = required_matches * 2 + recommended_matches
            scores[role] = total
        
        if scores:
            best_role = max(scores, key=scores.get)
            return best_role
        
        return 'software_engineer'  # Default
    
    def _analyze_skill_gaps(
        self,
        skills: List[str],
        target_role: str
    ) -> List[SkillGap]:
        """Analyze skill gaps for target role."""
        skill_set = set(s.lower() for s in skills)
        gaps = []
        
        if target_role not in INDUSTRY_SKILLS:
            return gaps
        
        role_skills = INDUSTRY_SKILLS[target_role]
        
        # Check required skills
        for skill in role_skills['required']:
            if skill.lower() not in skill_set:
                gaps.append(SkillGap(
                    skill=skill,
                    priority='required',
                    reason=f"Essential for {target_role.replace('_', ' ')} roles",
                    learning_resources=self._get_learning_resources(skill)
                ))
        
        # Check recommended skills
        for skill in role_skills['recommended']:
            if skill.lower() not in skill_set:
                gaps.append(SkillGap(
                    skill=skill,
                    priority='recommended',
                    reason=f"Strongly recommended for competitive candidates",
                    learning_resources=self._get_learning_resources(skill)
                ))
        
        # Sort by priority
        priority_order = {'required': 0, 'recommended': 1, 'nice_to_have': 2}
        gaps.sort(key=lambda x: priority_order.get(x.priority, 2))
        
        return gaps
    
    def _get_learning_resources(self, skill: str) -> List[str]:
        """Get learning resource suggestions for a skill."""
        resources = {
            'python': ['Python Official Docs', 'Real Python', 'Codecademy Python'],
            'java': ['Oracle Java Tutorials', 'Baeldung', 'JetBrains Academy'],
            'javascript': ['MDN Web Docs', 'JavaScript.info', 'Frontend Masters'],
            'react': ['React Documentation', 'React Tutorial', 'Epic React'],
            'docker': ['Docker Official Tutorial', 'Docker Playground', 'Docker Curriculum'],
            'kubernetes': ['Kubernetes Documentation', 'Kube Academy', 'Killercoda'],
            'aws': ['AWS Training', 'A Cloud Guru', 'Stephane Maarek Courses'],
            'machine learning': ['Andrew Ng ML Course', 'Scikit-learn Tutorial', 'Kaggle Learn'],
            'sql': ['SQLZoo', 'Mode SQL Tutorial', 'LeetCode SQL'],
            'git': ['Git Documentation', 'Atlassian Git Tutorial', 'Git Immersion'],
            'sql': ['SQLZoo', 'Mode SQL Tutorial', 'LeetCode SQL'],
        }
        
        return resources.get(skill.lower(), [f"Online courses for {skill}", "YouTube tutorials", "Documentation"])
    
    def _analyze_strengths(
        self,
        parsed_resume: Dict,
        skills: List[str],
        target_role: str
    ) -> List[ResumeStrength]:
        """Analyze resume strengths."""
        strengths = []
        
        # Check education
        education = parsed_resume.get('education', [])
        if education:
            degrees = [e.get('degree', '').upper() for e in education]
            if any('PHD' in d or 'DOCTOR' in d for d in degrees if d):
                strengths.append(ResumeStrength(
                    category='education',
                    description='Advanced degree (PhD/Doctorate)',
                    impact='Demonstrates deep expertise and research capabilities'
                ))
            if any('MASTER' in d for d in degrees if d):
                strengths.append(ResumeStrength(
                    category='education',
                    description='Master\'s degree',
                    impact='Indicates advanced knowledge and specialization'
                ))
        
        # Check certifications
        certifications = parsed_resume.get('certifications', [])
        if len(certifications) >= 3:
            strengths.append(ResumeStrength(
                category='certifications',
                description=f'{len(certifications)} professional certifications',
                impact='Shows commitment to continuous learning'
            ))
        
        # Check projects
        projects = parsed_resume.get('projects', [])
        if len(projects) >= 3:
            strengths.append(ResumeStrength(
                category='projects',
                description=f'{len(projects)} projects showcasing practical skills',
                impact='Demonstrates hands-on experience and initiative'
            ))
        
        # Check achievements
        achievements = parsed_resume.get('achievements', [])
        if len(achievements) >= 2:
            strengths.append(ResumeStrength(
                category='achievements',
                description=f'{len(achievements)} notable achievements',
                impact='Highlights measurable contributions and impact'
            ))
        
        # Check relevant skills
        role_skills = INDUSTRY_SKILLS.get(target_role, {})
        required_skills = [s.lower() for s in role_skills.get('required', [])]
        matched_skills = [s.lower() for s in skills if s.lower() in required_skills]
        
        if len(matched_skills) >= 5:
            strengths.append(ResumeStrength(
                category='skills',
                description=f'Strong foundation in {len(matched_skills)} core technologies',
                impact='Meets primary requirements for the role'
            ))
        
        # Check experience
        experience = parsed_resume.get('experience', [])
        total_years = 0
        for exp in experience:
            if exp.get('current'):
                # Estimate current duration
                total_years += 1.5
        
        if total_years >= 3:
            strengths.append(ResumeStrength(
                category='experience',
                description=f'{total_years}+ years of relevant experience',
                impact='Brings valuable industry experience'
            ))
        
        return strengths
    
    def _analyze_weaknesses(
        self,
        parsed_resume: Dict,
        skills: List[str],
        target_role: str
    ) -> List[ResumeWeakness]:
        """Analyze resume weaknesses."""
        weaknesses = []
        
        personal_info = parsed_resume.get('personal_info', {})
        
        # Check missing contact info
        if not personal_info.get('email'):
            weaknesses.append(ResumeWeakness(
                category='contact',
                issue='Missing email address',
                severity='high',
                suggestion='Add a professional email address'
            ))
        
        if not personal_info.get('phone'):
            weaknesses.append(ResumeWeakness(
                category='contact',
                issue='Missing phone number',
                severity='high',
                suggestion='Add a contact phone number'
            ))
        
        # Check LinkedIn
        if not personal_info.get('linkedin'):
            weaknesses.append(ResumeWeakness(
                category='online_presence',
                issue='No LinkedIn profile link',
                severity='medium',
                suggestion='Add a professional LinkedIn profile'
            ))
        
        # Check GitHub
        if not personal_info.get('github') and target_role in [
            'software_engineer', 'full_stack_developer', 'backend_developer', 'ml_engineer'
        ]:
            weaknesses.append(ResumeWeakness(
                category='online_presence',
                issue='No GitHub profile link',
                severity='medium',
                suggestion='Add a GitHub profile with portfolio projects'
            ))
        
        # Check education
        education = parsed_resume.get('education', [])
        if not education:
            weaknesses.append(ResumeWeakness(
                category='education',
                issue='No education section found',
                severity='high',
                suggestion='Add your educational background'
            ))
        
        # Check experience
        experience = parsed_resume.get('experience', [])
        if not experience:
            weaknesses.append(ResumeWeakness(
                category='experience',
                issue='No work experience section found',
                severity='high',
                suggestion='Add relevant work experience or internships'
            ))
        
        # Check skills
        if len(skills) < 5:
            weaknesses.append(ResumeWeakness(
                category='skills',
                issue=f'Only {len(skills)} skills listed',
                severity='medium',
                suggestion='Add more relevant technical skills'
            ))
        
        # Check certifications
        certifications = parsed_resume.get('certifications', [])
        if len(certifications) == 0:
            weaknesses.append(ResumeWeakness(
                category='certifications',
                issue='No professional certifications',
                severity='low',
                suggestion='Consider adding relevant certifications'
            ))
        
        # Check for keyword optimization
        role_skills = INDUSTRY_SKILLS.get(target_role, {})
        required_skills = [s.lower() for s in role_skills.get('required', [])]
        matched_skills = [s.lower() for s in skills if s.lower() in required_skills]
        
        if len(matched_skills) < 3:
            weaknesses.append(ResumeWeakness(
                category='ats_optimization',
                issue='Limited alignment with job keywords',
                severity='medium',
                suggestion='Optimize resume with more relevant keywords'
            ))
        
        # Check projects
        projects = parsed_resume.get('projects', [])
        if len(projects) == 0:
            weaknesses.append(ResumeWeakness(
                category='projects',
                issue='No projects section',
                severity='medium',
                suggestion='Add personal or academic projects'
            ))
        
        return weaknesses
    
    def _calculate_overall_score(
        self,
        parsed_resume: Dict,
        strengths: List[ResumeStrength],
        weaknesses: List[ResumeWeakness]
    ) -> float:
        """Calculate overall resume score (0-10)."""
        score = 10.0
        
        # Deduct for weaknesses
        for weakness in weaknesses:
            if weakness.severity == 'high':
                score -= 1.0
            elif weakness.severity == 'medium':
                score -= 0.5
            else:
                score -= 0.25
        
        # Add for strengths
        for strength in strengths:
            if 'degree' in strength.category.lower():
                score += 0.3
            elif 'certification' in strength.category.lower():
                score += 0.2
            elif 'project' in strength.category.lower():
                score += 0.2
        
        # Ensure score is in range
        return max(0.0, min(10.0, round(score, 1)))
    
    def _calculate_readiness_percentage(
        self,
        skill_gaps: List[SkillGap],
        weaknesses: List[ResumeWeakness],
        parsed_resume: Dict
    ) -> float:
        """Calculate interview readiness percentage."""
        score = 100.0
        
        # Deduct for required skill gaps
        required_gaps = [g for g in skill_gaps if g.priority == 'required']
        score -= len(required_gaps) * 8
        
        # Deduct for recommended skill gaps
        recommended_gaps = [g for g in skill_gaps if g.priority == 'recommended']
        score -= len(recommended_gaps) * 3
        
        # Deduct for high severity weaknesses
        high_weaknesses = [w for w in weaknesses if w.severity == 'high']
        score -= len(high_weaknesses) * 5
        
        # Deduct for medium severity weaknesses
        medium_weaknesses = [w for w in weaknesses if w.severity == 'medium']
        score -= len(medium_weaknesses) * 2
        
        # Ensure percentage is in range
        return max(0, min(100, round(score)))
    
    def _generate_recommendations(
        self,
        skill_gaps: List[SkillGap],
        weaknesses: List[ResumeWeakness],
        parsed_resume: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Address high priority gaps first
        required_gaps = [g for g in skill_gaps if g.priority == 'required']
        for gap in required_gaps[:3]:
            recommendations.append(
                f"Learn {gap.skill} - {gap.reason}"
            )
        
        # Address high severity weaknesses
        high_weaknesses = [w for w in weaknesses if w.severity == 'high']
        for weakness in high_weaknesses[:3]:
            recommendations.append(weakness.suggestion)
        
        # Address recommended gaps
        recommended_gaps = [g for g in skill_gaps if g.priority == 'recommended']
        for gap in recommended_gaps[:3]:
            recommendations.append(
                f"Consider learning {gap.skill} to strengthen your profile"
            )
        
        # Add general recommendations
        recommendations.extend([
            "Quantify achievements with metrics and numbers",
            "Use action verbs to describe responsibilities",
            "Tailor resume for each job application",
            "Ensure consistent formatting throughout",
            "Proofread for grammatical errors"
        ])
        
        return recommendations
    
    def _create_learning_path(
        self,
        skill_gaps: List[SkillGap]
    ) -> Dict[str, List[str]]:
        """Create a structured learning path."""
        learning_path = {
            'immediate': [],  # Must learn
            'short_term': [],  # Learn in 1-3 months
            'long_term': []    # Learn in 3-6 months
        }
        
        for gap in skill_gaps:
            if gap.priority == 'required':
                learning_path['immediate'].append(gap.skill)
            elif gap.priority == 'recommended':
                learning_path['short_term'].append(gap.skill)
            else:
                learning_path['long_term'].append(gap.skill)
        
        return learning_path
    
    def _get_ai_insights(
        self,
        parsed_resume: Dict,
        target_role: str
    ) -> Dict[str, Any]:
        """Get AI-enhanced insights."""
        try:
            prompt = f"""
            Analyze this resume for a {target_role.replace('_', ' ')} position.
            
            Resume Data:
            {json.dumps(parsed_resume, indent=2)}
            
            Provide:
            1. 3 additional strengths with specific examples
            2. 3 additional weaknesses with specific suggestions
            3. 3 additional recommendations
            
            Format as JSON with keys: additional_strengths, additional_weaknesses, additional_recommendations
            """
            
            response = self.analysis_model.generate_content(prompt)
            response_text = response.text
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        
        except Exception as e:
            logger.warning(f"AI insights generation failed: {e}")
        
        return {
            'additional_strengths': [],
            'additional_weaknesses': [],
            'additional_recommendations': []
        }
    
    def _to_dict(self, result: AnalysisResult) -> Dict[str, Any]:
        """Convert analysis result to dictionary."""
        return {
            'target_role': result.target_role,
            'skill_gaps': [asdict(g) for g in result.skill_gaps],
            'strengths': [asdict(s) for s in result.strengths],
            'weaknesses': [asdict(w) for w in result.weaknesses],
            'overall_score': result.overall_score,
            'readiness_percentage': result.readiness_percentage,
            'key_recommendations': result.key_recommendations,
            'learning_path': result.learning_path
        }


def analyze_resume(
    parsed_resume: Dict[str, Any],
    target_role: Optional[str] = None,
    target_companies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Convenience function to analyze a resume."""
    analyzer = ResumeAnalyzer()
    return analyzer.analyze(parsed_resume, target_role, target_companies)
