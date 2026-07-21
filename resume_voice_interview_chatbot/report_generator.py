"""
Report Generator Module
=======================
Generates comprehensive interview reports including
scores, feedback, analytics, and PDF export.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from loguru import logger

import config


@dataclass
class InterviewReport:
    """Complete interview report."""
    session_id: str
    candidate_name: str
    target_role: str
    company_mode: str
    interview_date: str
    
    # Overall metrics
    overall_score: float
    interview_readiness: float
    
    # Category scores
    hr_score: float
    technical_score: float
    communication_score: float
    project_score: float
    confidence_score: float
    resume_quality_score: float
    
    # Performance analysis
    strong_areas: List[str]
    weak_areas: List[str]
    topics_to_revise: List[str]
    
    # Recommendations
    learning_path: Dict[str, List[str]]
    key_recommendations: List[str]
    
    # Q&A Summary
    questions_summary: List[Dict[str, Any]]
    
    # Hiring recommendation
    hiring_recommendation: str
    recommendation_reason: str


class ReportGenerator:
    """Generates interview reports."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize report generator."""
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
                        'temperature': 0.3,
                        'max_output_tokens': 4096
                    }
                )
                logger.info("Gemini AI initialized for report generation")
        except Exception as e:
            logger.warning(f"AI initialization failed: {e}")
    
    def generate_report(
        self,
        memory_data: Dict[str, Any],
        resume_data: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> InterviewReport:
        """
        Generate comprehensive interview report.
        
        Args:
            memory_data: Interview memory data
            resume_data: Parsed resume data
            category_scores: Calculated category scores
            
        Returns:
            InterviewReport instance
        """
        logger.info("Generating interview report...")
        
        # Extract candidate info
        personal_info = resume_data.get('personal_info', {})
        candidate_name = personal_info.get('name', 'Candidate')
        
        # Calculate overall score
        scores = memory_data.get('questions', [])
        total_score = sum(q.get('score', 0) for q in scores if q.get('score'))
        question_count = len([q for q in scores if q.get('score')])
        overall_score = round(total_score / question_count, 2) if question_count > 0 else 0
        
        # Calculate interview readiness
        interview_readiness = self._calculate_readiness(
            overall_score, category_scores, memory_data
        )
        
        # Analyze performance
        strong_areas = self._analyze_strong_areas(scores, category_scores)
        weak_areas = self._analyze_weak_areas(scores, category_scores)
        topics_to_revise = self._get_topics_to_revise(weak_areas)
        
        # Generate recommendations
        learning_path = self._generate_learning_path(weak_areas, resume_data)
        key_recommendations = self._generate_recommendations(
            strong_areas, weak_areas, overall_score
        )
        
        # Hiring recommendation
        hiring_recommendation, recommendation_reason = self._get_hiring_recommendation(
            overall_score, category_scores, interview_readiness
        )
        
        # Questions summary
        questions_summary = self._summarize_questions(scores)
        
        # Create report
        report = InterviewReport(
            session_id=memory_data.get('session_id', ''),
            candidate_name=candidate_name,
            target_role=memory_data.get('target_role', 'Software Engineer'),
            company_mode=memory_data.get('company_mode', 'General'),
            interview_date=memory_data.get('completed_at', datetime.now().isoformat()),
            overall_score=overall_score,
            interview_readiness=interview_readiness,
            hr_score=category_scores.get('hr', overall_score),
            technical_score=category_scores.get('technical', overall_score),
            communication_score=category_scores.get('communication', overall_score),
            project_score=category_scores.get('projects', overall_score),
            confidence_score=self._calculate_confidence_score(scores),
            resume_quality_score=resume_data.get('analysis', {}).get('overall_score', 7.0),
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            topics_to_revise=topics_to_revise,
            learning_path=learning_path,
            key_recommendations=key_recommendations,
            questions_summary=questions_summary,
            hiring_recommendation=hiring_recommendation,
            recommendation_reason=recommendation_reason
        )
        
        logger.info(f"Report generated: {candidate_name}, Score: {overall_score}")
        return report
    
    def _calculate_readiness(
        self,
        overall_score: float,
        category_scores: Dict[str, float],
        memory_data: Dict[str, Any]
    ) -> float:
        """Calculate interview readiness percentage."""
        score_component = overall_score * 40
        
        # Category coverage bonus
        coverage = len([s for s in category_scores.values() if s > 0]) / 7 * 20
        
        # Progress bonus
        questions_asked = memory_data.get('questions_asked', 0)
        progress = min(questions_asked / config.interview_config.min_questions, 1.0) * 20
        
        # Confidence bonus
        confidence = memory_data.get('topic_analysis', {})
        strong_count = sum(1 for t in confidence.values() 
                         if t.get('performance_status') == 'strong')
        confidence_bonus = strong_count * 5
        
        readiness = score_component + coverage + progress + confidence_bonus
        return max(0, min(100, round(readiness)))
    
    def _analyze_strong_areas(
        self,
        scores: List[Dict],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Identify strong performance areas."""
        strong_areas = []
        
        # Check category scores
        for category, score in category_scores.items():
            if score >= 7.5:
                category_names = {
                    'hr': 'HR and Behavioral Questions',
                    'technical': 'Technical Knowledge',
                    'communication': 'Communication Skills',
                    'projects': 'Project Experience',
                    'programming': 'Programming Skills',
                    'sql': 'Database Knowledge',
                    'python': 'Python Programming',
                    'ml': 'Machine Learning',
                    'behavioral': 'Behavioral Responses'
                }
                strong_areas.append(category_names.get(category, category.title()))
        
        # Check topic analysis
        for q in scores:
            if q.get('score', 0) >= 8.0:
                if q.get('category') == 'hr' and 'HR Skills' not in strong_areas:
                    strong_areas.append('HR and Interpersonal Skills')
                elif q.get('category') == 'technical' and 'Technical Depth' not in strong_areas:
                    strong_areas.append('Technical Problem Solving')
        
        return strong_areas[:5]  # Top 5
    
    def _analyze_weak_areas(
        self,
        scores: List[Dict],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Identify weak performance areas."""
        weak_areas = []
        
        # Check category scores
        for category, score in category_scores.items():
            if 0 < score < 6.0:
                category_names = {
                    'hr': 'HR and Behavioral Responses',
                    'technical': 'Technical Knowledge',
                    'communication': 'Communication Clarity',
                    'projects': 'Project Description Skills',
                    'programming': 'Programming Fundamentals',
                    'sql': 'Database Concepts',
                    'python': 'Python Proficiency',
                    'ml': 'Machine Learning Concepts',
                    'behavioral': 'Behavioral Storytelling'
                }
                weak_areas.append(category_names.get(category, category.title()))
        
        return weak_areas[:5]  # Top 5
    
    def _get_topics_to_revise(self, weak_areas: List[str]) -> List[str]:
        """Get specific topics to revise."""
        topic_mapping = {
            'HR and Behavioral Responses': [
                'STAR method for behavioral questions',
                'Company research and cultural fit',
                'Career goals articulation'
            ],
            'Technical Knowledge': [
                'Core computer science fundamentals',
                'System design principles',
                'Data structures and algorithms'
            ],
            'Communication Clarity': [
                'Structuring technical explanations',
                'Using analogies for complex concepts',
                'Active listening skills'
            ],
            'Python Proficiency': [
                'Python best practices',
                'Common libraries and frameworks',
                'Code optimization techniques'
            ],
            'Database Concepts': [
                'SQL queries and joins',
                'Database normalization',
                'Query optimization'
            ],
            'Machine Learning Concepts': [
                'ML algorithms and use cases',
                'Model evaluation metrics',
                'Feature engineering basics'
            ]
        }
        
        topics = []
        for area in weak_areas:
            if area in topic_mapping:
                topics.extend(topic_mapping[area][:2])
        
        return topics[:8]  # Top 8 topics
    
    def _calculate_confidence_score(self, scores: List[Dict]) -> float:
        """Calculate confidence score based on performance variance."""
        valid_scores = [q.get('score', 0) for q in scores if q.get('score')]
        
        if not valid_scores:
            return 0.0
        
        # Higher confidence if scores are consistent
        avg = sum(valid_scores) / len(valid_scores)
        
        # Simple variance check
        if len(valid_scores) < 3:
            return avg
        
        variance = sum((s - avg) ** 2 for s in valid_scores) / len(valid_scores)
        
        if variance < 2:
            confidence = avg  # Consistent performance
        else:
            confidence = avg * 0.9  # Inconsistent
        
        return round(confidence, 2)
    
    def _generate_learning_path(
        self,
        weak_areas: List[str],
        resume_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate personalized learning path."""
        learning_path = {
            'immediate': [],  # Week 1-2
            'short_term': [],  # Month 1
            'long_term': []    # Months 2-3
        }
        
        # Map weak areas to learning resources
        resources = {
            'Technical Knowledge': [
                'CS Fundamentals Course',
                'System Design Primer',
                'Practice coding problems'
            ],
            'Python Proficiency': [
                'Python Documentation',
                'Real Python Tutorials',
                'Build small projects'
            ],
            'Database Concepts': [
                'SQL Tutorial',
                'Database Design Course',
                'Practice with sample databases'
            ],
            'Machine Learning Concepts': [
                'Andrew Ng ML Course',
                'Kaggle Micro-Courses',
                'Build a portfolio project'
            ],
            'Communication Skills': [
                'Technical writing practice',
                'Presentation skills',
                'Explain concepts to others'
            ],
            'HR and Behavioral Responses': [
                'Research STAR method',
                'Practice common questions',
                'Mock interviews'
            ]
        }
        
        for area in weak_areas:
            if area in resources:
                learning_path['immediate'].extend(resources[area][:1])
                learning_path['short_term'].extend(resources[area][1:2])
        
        # Remove duplicates while preserving order
        for key in learning_path:
            seen = set()
            unique = []
            for item in learning_path[key]:
                if item not in seen:
                    seen.add(item)
                    unique.append(item)
            learning_path[key] = unique
        
        return learning_path
    
    def _generate_recommendations(
        self,
        strong_areas: List[str],
        weak_areas: List[str],
        overall_score: float
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Overall recommendations based on score
        if overall_score >= 8.0:
            recommendations.append("Excellent performance! Focus on maintaining consistency.")
        elif overall_score >= 7.0:
            recommendations.append("Good performance. Target weak areas for improvement.")
        elif overall_score >= 6.0:
            recommendations.append("Average performance. Prioritize technical skill development.")
        else:
            recommendations.append("Focus on fundamentals before advanced topics.")
        
        # Specific recommendations
        if 'Technical Knowledge' in weak_areas or 'Python Proficiency' in weak_areas:
            recommendations.append("Strengthen coding fundamentals with daily practice.")
        
        if 'Communication Skills' in weak_areas or 'Communication Clarity' in weak_areas:
            recommendations.append("Practice explaining technical concepts clearly.")
        
        if 'Database Concepts' in weak_areas:
            recommendations.append("Build database projects to gain practical experience.")
        
        if 'HR and Behavioral Responses' in weak_areas:
            recommendations.append("Prepare 5-10 STAR stories from your experience.")
        
        # General recommendations
        recommendations.extend([
            "Review your resume for consistency and clarity.",
            "Practice mock interviews with peers or mentors.",
            "Research target companies' interview processes.",
            "Prepare thoughtful questions for the interviewer."
        ])
        
        return recommendations[:10]  # Top 10
    
    def _get_hiring_recommendation(
        self,
        overall_score: float,
        category_scores: Dict[str, float],
        readiness: float
    ) -> tuple:
        """Determine hiring recommendation."""
        # Calculate weighted recommendation score
        technical_score = category_scores.get('technical', overall_score)
        communication_score = category_scores.get('communication', overall_score)
        
        # Amazon-style leadership principle check
        all_scores = list(category_scores.values()) + [overall_score]
        min_score = min(all_scores)
        
        if overall_score >= 8.5 and readiness >= 80:
            return "Strong Hire", "Exceptional performance across all areas."
        elif overall_score >= 7.5 and technical_score >= 7.0:
            return "Hire", "Strong technical skills with good communication."
        elif overall_score >= 6.5:
            return "Consider", "Good potential with room for growth. Recommend further evaluation."
        elif overall_score >= 5.5 and min_score >= 4.0:
            return "Weak Consider", "Shows basic competence. Consider for junior roles or training programs."
        elif overall_score >= 4.0:
            return "No Hire", "Below expectations. Recommend additional preparation before reapplying."
        else:
            return "No Hire", "Significant gaps identified. Focus on fundamentals and retry."
    
    def _summarize_questions(self, scores: List[Dict]) -> List[Dict[str, Any]]:
        """Summarize questions and answers."""
        summary = []
        
        for q in scores:
            summary.append({
                'number': q.get('question_id', 0),
                'question': q.get('question_text', ''),
                'category': q.get('category', ''),
                'difficulty': q.get('difficulty', 'medium'),
                'score': q.get('score', 0),
                'strengths': q.get('strengths', [])[:2],
                'improvements': q.get('weaknesses', [])[:2]
            })
        
        return summary
    
    def to_dict(self, report: InterviewReport) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(report)
    
    def to_json(self, report: InterviewReport) -> str:
        """Convert report to JSON string."""
        return json.dumps(asdict(report), indent=2)
    
    def export_pdf(
        self,
        report: InterviewReport,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Export report as PDF.
        
        Args:
            report: InterviewReport instance
            output_path: Optional output path
            
        Returns:
            Path to generated PDF
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            logger.error("reportlab not installed for PDF generation")
            return None
        
        if output_path is None:
            output_path = config.REPORTS_DIR / f"interview_report_{report.session_id}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Title
        story.append(Paragraph("Interview Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Candidate Info
        story.append(Paragraph(f"<b>Candidate:</b> {report.candidate_name}", body_style))
        story.append(Paragraph(f"<b>Target Role:</b> {report.target_role}", body_style))
        story.append(Paragraph(f"<b>Company Mode:</b> {report.company_mode}", body_style))
        story.append(Paragraph(f"<b>Date:</b> {report.interview_date[:10]}", body_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Overall Score
        story.append(Paragraph("Overall Performance", heading_style))
        
        score_data = [
            ['Metric', 'Score'],
            ['Overall Score', f"{report.overall_score}/10"],
            ['Interview Readiness', f"{report.interview_readiness}%"],
            ['HR Score', f"{report.hr_score}/10"],
            ['Technical Score', f"{report.technical_score}/10"],
            ['Communication Score', f"{report.communication_score}/10"],
        ]
        
        score_table = Table(score_data, colWidths=[2.5 * inch, 1.5 * inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Strong Areas
        if report.strong_areas:
            story.append(Paragraph("Strengths", heading_style))
            for area in report.strong_areas:
                story.append(Paragraph(f"• {area}", body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Weak Areas
        if report.weak_areas:
            story.append(Paragraph("Areas for Improvement", heading_style))
            for area in report.weak_areas:
                story.append(Paragraph(f"• {area}", body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Topics to Revise
        if report.topics_to_revise:
            story.append(Paragraph("Topics to Revise", heading_style))
            for topic in report.topics_to_revise:
                story.append(Paragraph(f"• {topic}", body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Recommendations
        if report.key_recommendations:
            story.append(Paragraph("Recommendations", heading_style))
            for rec in report.key_recommendations[:5]:
                story.append(Paragraph(f"• {rec}", body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Hiring Recommendation
        story.append(Paragraph("Hiring Recommendation", heading_style))
        
        rec_color = colors.green if 'Hire' in report.hiring_recommendation else colors.red
        rec_data = [
            [Paragraph(f"<b>{report.hiring_recommendation}</b>", 
                      ParagraphStyle('RecStyle', fontSize=14, textColor=rec_color))],
            [Paragraph(report.recommendation_reason, body_style)]
        ]
        rec_table = Table(rec_data, colWidths=[5 * inch])
        rec_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(rec_table)
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF report saved to: {output_path}")
        
        return output_path
    
    def generate_and_export(
        self,
        memory_data: Dict[str, Any],
        resume_data: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> tuple:
        """Generate report and export PDF."""
        report = self.generate_report(memory_data, resume_data, category_scores)
        pdf_path = self.export_pdf(report)
        
        return self.to_dict(report), pdf_path


def generate_interview_report(
    memory_data: Dict[str, Any],
    resume_data: Dict[str, Any],
    category_scores: Dict[str, float]
) -> Dict[str, Any]:
    """Convenience function to generate report."""
    generator = ReportGenerator()
    report = generator.generate_report(memory_data, resume_data, category_scores)
    return generator.to_dict(report)
