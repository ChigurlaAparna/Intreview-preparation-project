"""
Resume Voice Interview Chatbot
=============================
Main Streamlit application for AI-powered voice interview preparation.
Enhanced UI with attractive, visible, and user-friendly design.
"""

import streamlit as st
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
import config
from database import db
from resume_parser import ResumeParser
from resume_analyzer import ResumeAnalyzer
from question_generator import QuestionGenerator, InterviewQuestion
from voice_input import VoiceInput, AudioRecorder
from voice_output import VoiceOutput
from answer_evaluator import AnswerEvaluator
from memory import memory_manager, create_interview_memory
from report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="AI Voice Interview Coach",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Beautiful Attractive Design
st.markdown("""
<style>
    /* ====== MAIN THEME - Beautiful Gradient Background ====== */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
        min-height: 100vh;
    }
    
    /* ====== TEXT COLORS ====== */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a2e !important;
    }
    
    p, span, div {
        color: #333 !important;
    }
    
    /* ====== BEAUTIFUL HEADER ====== */
    .main-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%) !important;
        padding: 35px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 15px 45px rgba(255, 107, 107, 0.4) !important;
        border: 3px solid white;
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.8rem !important;
        margin: 0 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        font-weight: 800 !important;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95) !important;
        font-size: 1.3rem !important;
        margin-top: 15px !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    
    /* ====== RAINBOW CARDS ====== */
    .metric-card {
        background: linear-gradient(145deg, #ff6b6b, #feca57) !important;
        border-radius: 20px !important;
        padding: 30px 20px !important;
        text-align: center;
        margin: 15px 0 !important;
        box-shadow: 0 10px 35px rgba(255, 107, 107, 0.35) !important;
        border: none !important;
        transition: all 0.4s ease !important;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.05) !important;
        box-shadow: 0 20px 50px rgba(255, 107, 107, 0.5) !important;
    }
    
    .metric-card h3 {
        color: white !important;
        font-size: 3rem !important;
        margin: 0 !important;
        font-weight: 900 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-card p {
        color: rgba(255,255,255,0.95) !important;
        margin: 10px 0 0 0 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* ====== COLORFUL BUTTONS ====== */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%) !important;
        color: white !important;
        border: none !important;
        padding: 18px 35px !important;
        border-radius: 50px !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 15px 40px rgba(255, 107, 107, 0.5) !important;
        background: linear-gradient(135deg, #ff5252 0%, #ffab40 50%, #18b6f6 100%) !important;
    }
    
    /* ====== QUESTION BOX - Rainbow Border ====== */
    .question-box {
        background: white !important;
        border-radius: 20px !important;
        padding: 30px !important;
        margin: 25px 0 !important;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15) !important;
        border-left: 8px solid transparent !important;
        border-image: linear-gradient(180deg, #ff6b6b, #feca57, #48dbfb, #a55eea) 1 !important;
    }
    
    .question-box h4 {
        color: #1a1a2e !important;
        font-size: 1.5rem !important;
        margin: 0 !important;
        font-weight: 700 !important;
    }
    
    /* ====== BEAUTIFUL TABS ====== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: white !important;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #667eea22, #764ba222) !important;
        border-radius: 50px !important;
        padding: 15px 30px !important;
        color: #333 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border: 2px solid #eee;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #667eea44, #764ba244) !important;
        transform: scale(1.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4) !important;
    }
    
    /* ====== METRICS - Glowing ====== */
    [data-testid="stMetric"] {
        background: white !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12) !important;
        border: 3px solid transparent !important;
        background-clip: padding-box;
        position: relative;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: -3px; left: -3px; right: -3px; bottom: -3px;
        background: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb, #a55eea);
        border-radius: 22px;
        z-index: -1;
    }
    
    [data-testid="stMetricLabel"] {
        color: #666 !important;
        font-size: 1.1rem !important;
        font-weight: 600;
    }
    
    [data-testid="stMetricValue"] {
        color: linear-gradient(135deg, #ff6b6b, #feca57) !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #ff6b6b, #feca57) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* ====== INPUTS - Soft & Modern ====== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: white !important;
        border: 3px solid #e0e0e0 !important;
        border-radius: 15px !important;
        padding: 16px 20px !important;
        font-size: 1.15rem;
        color: #333 !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #ff6b6b !important;
        box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.2) !important;
        outline: none;
    }
    
    /* ====== COLORFUL ALERTS ====== */
    .stSuccess {
        background: linear-gradient(135deg, #00d09c, #00b894) !important;
        border-radius: 15px;
        padding: 18px 25px;
        color: white !important;
        font-weight: 700;
        box-shadow: 0 5px 20px rgba(0, 217, 156, 0.4) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #ff6b6b, #ee5a5a) !important;
        border-radius: 15px;
        padding: 18px 25px;
        color: white !important;
        font-weight: 700;
        box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #feca57, #ffbe0b) !important;
        border-radius: 15px;
        padding: 18px 25px;
        color: #333 !important;
        font-weight: 700;
        box-shadow: 0 5px 20px rgba(254, 202, 87, 0.4) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #48dbfb, #0abde3) !important;
        border-radius: 15px;
        padding: 18px 25px;
        color: white !important;
        font-weight: 700;
        box-shadow: 0 5px 20px rgba(72, 219, 251, 0.4) !important;
    }
    
    /* ====== PROGRESS BAR - Rainbow ====== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #a55eea) !important;
        border-radius: 20px;
    }
    
    /* ====== HIDDEN ELEMENTS ====== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ====== SCROLLBAR - Rainbow ====== */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb) !important;
        border-radius: 10px;
    }
    
    /* ====== COMPANIES GRID - Colorful Pills ====== */
    .company-badge {
        background: linear-gradient(135deg, #ff6b6b22, #feca5722, #48dbfb22) !important;
        border: 3px solid !important;
        border-image: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb) 1 !important;
        border-radius: 50px !important;
        padding: 12px 22px !important;
        display: inline-block !important;
        margin: 8px !important;
        font-size: 1.05rem !important;
        color: #333 !important;
        font-weight: 700 !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease;
    }
    
    .company-badge:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3) !important;
    }
    
    /* ====== FEATURE CARDS - 3D Effect ====== */
    .feature-card {
        background: white !important;
        border-radius: 25px !important;
        padding: 35px 25px !important;
        text-align: center !important;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.12) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        border: 3px solid transparent;
        background-clip: padding-box;
        position: relative;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: -3px; left: -3px; right: -3px; bottom: -3px;
        background: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb, #a55eea);
        border-radius: 28px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card:hover {
        transform: translateY(-15px) scale(1.03) !important;
    }
    
    .feature-icon {
        font-size: 4rem !important;
        margin-bottom: 20px !important;
        filter: drop-shadow(0 5px 10px rgba(0,0,0,0.2));
    }
    
    .feature-card h4 {
        color: #1a1a2e !important;
        font-size: 1.4rem !important;
        margin-bottom: 12px !important;
        font-weight: 800 !important;
    }
    
    .feature-card p {
        color: #555 !important;
        margin: 0 !important;
        font-size: 1.05rem !important;
        line-height: 1.6;
    }
    
    /* ====== CARDS ====== */
    div[data-testid="stCard"] {
        background: white !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* ====== SELECTBOX ====== */
    .stSelectbox label, .stMultiSelect label {
        color: #333 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    
    /* ====== EXPANDER ====== */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 15px !important;
        font-weight: 700;
        color: #333 !important;
        border: 2px solid #eee;
        padding: 10px 15px;
    }
    
    /* ====== CHECKBOX ====== */
    .stCheckbox label {
        color: #333 !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    /* ====== DIVIDER ====== */
    hr {
        border: none;
        height: 4px;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #a55eea) !important;
        border-radius: 10px;
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== HELPER FUNCTIONS ====================

def render_header(title: str, subtitle: str = "", emoji: str = "🎤"):
    """Render a beautiful header."""
    st.markdown(f"""
    <div class="main-header">
        <h1>{emoji} {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str):
    """Render a styled metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <h3>{value}</h3>
        <p>{label}</p>
    </div>
    """, unsafe_allow_html=True)


def render_feature_card(icon: str, title: str, description: str):
    """Render a feature card."""
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <h4 style="color: #333; margin-bottom: 10px;">{title}</h4>
        <p style="color: #666; margin: 0;">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def render_question_box(question: str, category: str, difficulty: str):
    """Render a styled question box."""
    diff_color = {"easy": "#11998e", "medium": "#f2994a", "hard": "#eb3349"}.get(difficulty.lower(), "#667eea")
    st.markdown(f"""
    <div class="question-box">
        <h4>{question}</h4>
        <div style="margin-top: 15px;">
            <span class="company-badge" style="background: {diff_color}20; border-color: {diff_color}; color: {diff_color};">
                {category.upper()}
            </span>
            <span class="company-badge" style="background: {diff_color}20; border-color: {diff_color}; color: {diff_color};">
                {difficulty.upper()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_score_color(score: float) -> str:
    """Get color class based on score."""
    if score >= 8:
        return "#11998e"
    elif score >= 6:
        return "#f2994a"
    return "#eb3349"


# ==================== SESSION STATE ====================

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'user_id': None,
        'username': None,
        'logged_in': False,
        'current_page': 'Home',
        'resume_data': None,
        'resume_id': None,
        'analysis_data': None,
        'interview_session_id': None,
        'interview_memory': None,
        'current_question': None,
        'question_index': 0,
        'questions': [],
        'answers': [],
        'is_recording': False,
        'transcript': '',
        'voice_enabled': True,
        'selected_voice': 'en-US-AriaNeural',
        'company_mode': 'TCS'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==================== AUTHENTICATION ====================

def auth_page():
    """Authentication page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🎤 AI Voice Interview Coach")
        st.markdown("### Your Personal Interview Preparation Assistant")
        
        tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("### Login")
                username = st.text_input("Username or Email", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    if username and password:
                        user = db.authenticate_user(username, password)
                        if user:
                            st.session_state.user_id = user['id']
                            st.session_state.username = user['username']
                            st.session_state.logged_in = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.warning("Please fill all fields")
        
        with tab2:
            with st.form("register_form"):
                st.markdown("### Create Account")
                new_user = st.text_input("Username", key="reg_user")
                email = st.text_input("Email", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_pass")
                confirm_pass = st.text_input("Confirm Password", type="password")
                
                submitted = st.form_submit_button("Register", use_container_width=True)
                
                if submitted:
                    if new_user and email and password:
                        if password != confirm_pass:
                            st.error("Passwords don't match")
                        else:
                            try:
                                user_id = db.create_user(new_user, email, password)
                                st.success("Account created! Please login.")
                            except Exception as e:
                                st.error(f"Registration failed: {e}")
                    else:
                        st.warning("Please fill all fields")
        
        with tab3:
            with st.form("forgot_form"):
                st.markdown("### Reset Password")
                email = st.text_input("Email", key="forgot_email")
                
                submitted = st.form_submit_button("Send Reset Link", use_container_width=True)
                
                if submitted:
                    user = db.get_user_by_email(email)
                    if user:
                        token = db.create_password_reset_token(user['id'])
                        st.success(f"Reset token created: {token[:20]}...")
                    else:
                        st.info("If the email exists, a reset link has been sent.")


def logout():
    """Logout user."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()


# ==================== SIDEBAR NAVIGATION ====================

def render_sidebar():
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown("---")
        
        pages = [
            ("🏠", "Home", "home"),
            ("📄", "Resume Upload", "resume"),
            ("📊", "Resume Dashboard", "dashboard"),
            ("🎤", "Start Interview", "interview"),
            ("📝", "Interview History", "history"),
            ("⚙️", "Settings", "settings")
        ]
        
        for icon, name, page_id in pages:
            if st.button(f"{icon} {name}", key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()


# ==================== HOME PAGE ====================

def home_page():
    """Home page with overview and quick actions."""
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_header("Welcome to AI Interview Coach", "Your Personal AI-Powered Interview Preparation Assistant", "🎤")
        
        st.markdown("""
        <div style="background: rgba(255,255,255,0.95); padding: 25px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 20px 0;">
            <h3 style="color: #333; margin-top: 0;">🚀 Supercharge Your Interview Preparation</h3>
            <p style="color: #666; font-size: 1.1rem; line-height: 1.6;">
                Practice with our AI-powered voice interview system that adapts to your skill level, 
                provides real-time feedback, and helps you land your dream job at top companies.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.logged_in:
            stats = db.get_user_stats(st.session_state.user_id)
            
            st.markdown("### 📊 Your Progress")
            
            col_a, col_b = st.columns(2)
            with col_a:
                render_metric_card(str(stats['total_interviews']), "Total Interviews")
            with col_b:
                render_metric_card(f"{stats['average_score']}/10", "Avg Score")
            
            col_c, col_d = st.columns(2)
            with col_c:
                render_metric_card(str(stats['completed_interviews']), "Completed")
            with col_d:
                render_metric_card(str(stats['total_resumes']), "Resumes")
    
    # Features grid
    st.markdown("---")
    st.markdown("### ✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_feature_card("📄", "Resume Analysis", 
            "Upload your resume and get AI-powered analysis with skill gap identification")
    with col2:
        render_feature_card("🎤", "Voice Interviews", 
            "Practice with voice interaction - speak your answers naturally")
    with col3:
        render_feature_card("📊", "Real-time Feedback", 
            "Get instant feedback on your answers with detailed scoring")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        render_feature_card("📈", "Progress Tracking", 
            "Track your improvement over time with comprehensive reports")
    with col5:
        render_feature_card("🏢", "Company Modes", 
            "Practice for TCS, Infosys, Amazon, Google, and more")
    with col6:
        render_feature_card("📥", "PDF Reports", 
            "Download detailed interview reports for review")
    
    # Supported companies
    st.markdown("---")
    st.markdown("### 🏢 Practice for Top Companies")
    
    companies = [
        ("TCS", "🏢"), ("Infosys", "💻"), ("Accenture", "🌐"), 
        ("Deloitte", "📊"), ("Capgemini", "🔧"), ("Cognizant", "💡"),
        ("Microsoft", "🪟"), ("Amazon", "📦"), ("Google", "🔍")
    ]
    
    company_html = '<div style="text-align: center; margin: 20px 0;">'
    for name, icon in companies:
        company_html += f'<span class="company-badge">{icon} {name}</span>'
    company_html += '</div>'
    
    st.markdown(company_html, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Upload Resume", use_container_width=True):
            st.session_state.current_page = "resume"
            st.rerun()
    with col2:
        if st.button("🎤 Start Interview", use_container_width=True):
            st.session_state.current_page = "interview"
            st.rerun()
    with col3:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
    with col4:
        if st.button("📝 Interview History", use_container_width=True):
            st.session_state.current_page = "history"
            st.rerun()


# ==================== RESUME PAGE ====================

def resume_page():
    """Resume upload and analysis page."""
    render_header("Resume Upload & Analysis", "Upload your resume to get personalized interview questions", "📄")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.95); padding: 25px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-top: 0;">📤 Upload Your Resume</h3>
            <p style="color: #666;">Supported formats: PDF, DOCX</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Drag and drop your resume here",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            # Save file
            file_path = config.UPLOAD_DIR / f"{st.session_state.user_id}_{uploaded_file.name}"
            
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Parse and analyze
            with st.spinner("🔄 Parsing resume..."):
                try:
                    parser = ResumeParser()
                    parsed_data = parser.parse(file_path)
                    st.session_state.resume_data = parsed_data
                    
                    with st.spinner("🔄 Analyzing resume..."):
                        analyzer = ResumeAnalyzer()
                        analysis = analyzer.analyze(parsed_data)
                        st.session_state.analysis_data = analysis
                    
                    st.success("✅ Resume analyzed successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error processing resume: {e}")
    
    with col2:
        if st.session_state.resume_data:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.95); padding: 25px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);">
                <h3 style="color: #333; margin-top: 0;">📋 Extracted Information</h3>
            </div>
            """, unsafe_allow_html=True)
            
            personal = st.session_state.resume_data.get('personal_info', {})
            
            st.markdown(f"""
            <div style="background: rgba(102, 126, 234, 0.1); padding: 20px; border-radius: 12px; margin: 15px 0;">
                <p style="margin: 5px 0;"><strong>👤 Name:</strong> {personal.get('name', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>📧 Email:</strong> {personal.get('email', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>📱 Phone:</strong> {personal.get('phone', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Skills
            skills = st.session_state.resume_data.get('extracted_skills', [])
            if skills:
                st.markdown(f"""
                <div style="background: rgba(17, 153, 142, 0.1); padding: 20px; border-radius: 12px; margin: 15px 0;">
                    <h4 style="color: #333; margin: 0 0 10px 0;">🛠️ Skills ({len(skills)})</h4>
                    <p style="color: #666; margin: 0; line-height: 1.6;">
                        {', '.join(skills[:20])}{'...' if len(skills) > 20 else ''}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Stats
            col_a, col_b, col_c = st.columns(3)
            
            education = st.session_state.resume_data.get('education', [])
            experience = st.session_state.resume_data.get('experience', [])
            projects = st.session_state.resume_data.get('projects', [])
            
            with col_a:
                render_metric_card(str(len(education)), "Education")
            with col_b:
                render_metric_card(str(len(experience)), "Experience")
            with col_c:
                render_metric_card(str(len(projects)), "Projects")
    
    # Analysis results
    if st.session_state.analysis_data:
        st.markdown("---")
        
        analysis = st.session_state.analysis_data
        
        st.markdown("""
        <div style="background: rgba(255,255,255,0.95); padding: 25px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-top: 0;">📊 Resume Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Score cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Overall Score", f"{analysis.get('overall_score', 0)}/10")
        with col2:
            st.metric("🎯 Readiness", f"{analysis.get('readiness_percentage', 0)}%")
        with col3:
            st.metric("✅ Strengths", len(analysis.get('strengths', [])))
        with col4:
            st.metric("⚠️ Gaps", len(analysis.get('skill_gaps', [])))
        
        # Strengths and weaknesses
        col_left, col_right = st.columns(2)
        
        with col_left:
            if analysis.get('strengths'):
                st.markdown("#### ✅ Your Strengths")
                for strength in analysis['strengths'][:5]:
                    st.markdown(f"""
                    <div style="background: rgba(17, 153, 142, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #11998e;">
                        <strong>{strength.get('category', '')}</strong><br>
                        <small>{strength.get('description', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_right:
            if analysis.get('weaknesses'):
                st.markdown("#### ⚠️ Areas for Improvement")
                for weakness in analysis['weaknesses'][:5]:
                    st.markdown(f"""
                    <div style="background: rgba(235, 51, 73, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #eb3349;">
                        <strong>{weakness.get('issue', '')}</strong><br>
                        <small>{weakness.get('suggestion', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Learning path
        if analysis.get('learning_path'):
            st.markdown("#### 📚 Recommended Learning Path")
            
            learning = analysis['learning_path']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Immediate (Week 1-2)**")
                for item in learning.get('immediate', [])[:3]:
                    st.markdown(f"- 🔴 {item}")
            
            with col2:
                st.markdown("**Short-term (Month 1)**")
                for item in learning.get('short_term', [])[:3]:
                    st.markdown(f"- 🟡 {item}")
            
            with col3:
                st.markdown("**Long-term (Months 2-3)**")
                for item in learning.get('long_term', [])[:3]:
                    st.markdown(f"- 🟢 {item}")


# ==================== DASHBOARD PAGE ====================

def dashboard_page():
    """Resume dashboard page."""
    st.markdown("# 📊 Resume Dashboard")
    
    # Get user resumes
    resumes = db.get_user_resumes(st.session_state.user_id)
    
    if not resumes:
        st.info("No resumes uploaded yet. Go to Resume Upload to add one.")
        return
    
    # Display resumes
    for resume in resumes:
        with st.expander(f"📄 {resume['filename']} - {resume['uploaded_at'][:10]}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Parse stored data
                parsed = resume.get('parsed_data', {})
                if isinstance(parsed, str):
                    parsed = json.loads(parsed)
                
                skills = resume.get('extracted_skills', [])
                if isinstance(skills, str):
                    skills = json.loads(skills)
                
                st.markdown(f"**Skills:** {', '.join(skills[:20])}")
                
                analysis = resume.get('analysis', {})
                if isinstance(analysis, str):
                    analysis = json.loads(analysis)
                
                if analysis:
                    st.markdown(f"**Target Role:** {analysis.get('target_role', 'N/A')}")
                    st.markdown(f"**Overall Score:** {analysis.get('overall_score', 'N/A')}")
                    st.markdown(f"**Readiness:** {analysis.get('readiness_percentage', 'N/A')}%")
            
            with col2:
                if st.button("Use for Interview", key=f"use_{resume['id']}"):
                    st.session_state.resume_id = resume['id']
                    st.session_state.resume_data = parsed
                    if isinstance(resume.get('analysis'), str):
                        st.session_state.analysis_data = json.loads(resume['analysis'])
                    else:
                        st.session_state.analysis_data = resume.get('analysis', {})
                    st.success("Resume selected for interview!")
                
                if st.button("Delete", key=f"del_{resume['id']}"):
                    db.delete_resume(resume['id'])
                    st.rerun()


# ==================== INTERVIEW PAGE ====================

def interview_page():
    """Main interview page with FULL VOICE support - like ChatGPT voice."""
    
    # Initialize voice session state
    if 'voice_mode' not in st.session_state:
        st.session_state.voice_mode = True
    if 'is_speaking' not in st.session_state:
        st.session_state.is_speaking = False
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    
    # Check if resume is loaded
    if not st.session_state.resume_data:
        render_header("🎤 Voice Interview", "Setup your voice interview", "🎤")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b22, #feca5722); padding: 40px; border-radius: 20px; text-align: center; margin: 20px 0; border: 3px solid #ff6b6b;">
            <div style="font-size: 4rem; margin-bottom: 20px;">📄</div>
            <h2 style="color: #1a1a2e; margin: 0 0 15px 0;">Upload Your Resume First</h2>
            <p style="color: #666; font-size: 1.1rem;">Your resume helps us generate personalized interview questions</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Upload Resume", use_container_width=True):
                st.session_state.current_page = "resume"
                st.rerun()
        with col2:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        return
    
    # If no active interview, show setup
    if not st.session_state.interview_session_id:
        render_voice_setup()
    else:
        render_full_voice_interview()

def render_voice_setup():
    """Render voice interview setup screen."""
    render_header("🎤 Voice Interview Setup", "Configure your AI-powered voice interview", "🎤")
    
    # Voice Instructions
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea22, #764ba244); padding: 25px; border-radius: 20px; margin: 20px 0; border: 3px solid #667eea;">
        <h3 style="color: #1e3a8a; margin: 0 0 15px 0;">🎙️ How Voice Interview Works</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 15px;">
            <div style="flex: 1; min-width: 200px; background: white; padding: 15px; border-radius: 12px;">
                <div style="font-size: 2rem;">1️⃣</div>
                <h4 style="color: #333; margin: 10px 0 5px 0;">Questions Spoken Aloud</h4>
                <p style="color: #666; margin: 0;">Interview questions are automatically spoken</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: white; padding: 15px; border-radius: 12px;">
                <div style="font-size: 2rem;">2️⃣</div>
                <h4 style="color: #333; margin: 10px 0 5px 0;">Speak Your Answers</h4>
                <p style="color: #666; margin: 0;">Click mic and speak naturally</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: white; padding: 15px; border-radius: 12px;">
                <div style="font-size: 2rem;">3️⃣</div>
                <h4 style="color: #333; margin: 10px 0 5px 0;">AI Analyzes</h4>
                <p style="color: #666; margin: 0;">Get instant feedback on your answers</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings
    col1, col2 = st.columns([1, 1])
    
    with col1:
        company_mode = st.selectbox(
            "🏢 Target Company",
            ['TCS', 'INFOSYS', 'ACCENTURE', 'DELOITTE', 'CAPGEMINI', 
             'COGNIZANT', 'MICROSOFT', 'AMAZON', 'GOOGLE'],
            index=0
        )
        st.session_state.company_mode = company_mode
    
    with col2:
        num_q = st.slider("📝 Number of Questions", 5, 25, 10)
    
    # Voice settings
    st.markdown("### 🔊 Voice Settings")
    col_v1, col_v2, col_v3 = st.columns([1, 1, 1])
    
    with col_v1:
        st.session_state.voice_mode = st.checkbox("🎤 Enable Voice", value=True)
    
    with col_v2:
        voice_speed = st.selectbox("⚡ Speed", ["0.75x", "1x", "1.25x"], index=1)
    
    with col_v3:
        auto_next = st.checkbox("🔄 Auto-next on silence", value=False)
    
    st.markdown("---")
    
    # Start button
    if st.button("🚀 START VOICE INTERVIEW", use_container_width=True, type="primary"):
        start_new_interview(company_mode, num_q)

def render_full_voice_interview():
    """Render the full voice-first interview interface."""
    
    # Update session state
    memory = st.session_state.interview_memory
    questions = st.session_state.questions
    current_idx = st.session_state.question_index
    total = len(questions)
    
    if current_idx >= total:
        complete_interview()
        return
    
    current_q = questions[current_idx]
    progress = ((current_idx) / total) * 100
    
    # Header with progress
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 16px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="color: white; margin: 0;">🎤 Voice Interview</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">{st.session_state.company_mode} Mode</p>
            </div>
            <div style="text-align: right;">
                <h3 style="color: white; margin: 0;">{current_idx + 1}/{total}</h3>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">{int(progress)}% Complete</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    st.progress(progress / 100)
    
    # Question Card
    st.markdown(f"""
    <div style="background: white; padding: 30px; border-radius: 20px; margin: 20px 0; box-shadow: 0 8px 30px rgba(0,0,0,0.12); border-left: 6px solid #667eea;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <div>
                <span style="background: #667eea22; color: #667eea; padding: 5px 15px; border-radius: 20px; font-weight: 600; font-size: 0.9rem;">📂 {current_q.category}</span>
                <span style="background: #feca5722; color: #d97706; padding: 5px 15px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; margin-left: 10px;">📊 {current_q.difficulty.upper()}</span>
            </div>
            <button onclick="speakQuestion()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; font-size: 1rem;">🔊 Speak</button>
        </div>
        <h3 style="color: #1a1a2e; font-size: 1.4rem; line-height: 1.6; margin: 0;">{current_q.question_text}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Speak Question Button with Auto-Play
    if st.session_state.voice_mode:
        col_speak1, col_speak2 = st.columns([1, 1])
        
        with col_speak1:
            if st.button("🔊 SPEAK QUESTION", use_container_width=True):
                try:
                    with st.spinner("Generating audio..."):
                        voice = VoiceOutput()
                        audio_file = voice.generate_question_speech(
                            current_idx + 1,
                            current_q.question_text,
                            current_q.category,
                            current_q.difficulty
                        )
                        if audio_file:
                            st.audio(str(audio_file), format="audio/mp3", start_time=0)
                            st.success("✅ Question spoken! Audio should be playing above.")
                        else:
                            st.warning("Could not generate audio")
                except Exception as e:
                    st.error(f"Voice error: {e}")
        
        with col_speak2:
            st.markdown("")
            st.markdown("💡 *Make sure your volume is ON*")
    
    # Auto-speak first question
    if current_idx == 0 and st.session_state.voice_mode:
        with st.spinner("🔊 Speaking question..."):
            try:
                voice = VoiceOutput()
                audio_file = voice.generate_question_speech(
                    current_idx + 1,
                    current_q.question_text,
                    current_q.category,
                    current_q.difficulty
                )
                if audio_file:
                    st.audio(str(audio_file), format="audio/mp3", start_time=0)
            except:
                pass
    
    st.markdown("---")
    
    # Voice Answer Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #48dbfb22, #0abde322); padding: 25px; border-radius: 20px; margin: 20px 0; border: 3px solid #48dbfb;">
        <h3 style="color: #1a1a2e; margin: 0 0 15px 0;">🎤 Your Voice Answer</h3>
        <p style="color: #666; margin: 0 0 20px 0;">Click the microphone button and speak your answer</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Microphone Buttons
    col_mic1, col_mic2 = st.columns([1, 1])
    
    with col_mic1:
        mic_button_text = "🎤 START SPEAKING" if not st.session_state.is_listening else "⏹️ STOP & TRANSCRIBE"
        if st.button(mic_button_text, use_container_width=True, type="primary"):
            st.session_state.is_listening = not st.session_state.is_listening
            st.rerun()
    
    with col_mic2:
        if st.button("🔄 CLEAR", use_container_width=True):
            st.session_state.voice_answer_text = ""
            st.rerun()
    
    # Listening indicator
    if st.session_state.is_listening:
        st.markdown("""
        <div style="background: rgba(235, 51, 73, 0.15); padding: 30px; border-radius: 16px; text-align: center; margin: 20px 0; border: 3px solid #eb3349;">
            <div style="font-size: 4rem; animation: pulse 1s infinite;">🎙️</div>
            <h2 style="color: #eb3349; margin: 15px 0 5px 0;">LISTENING...</h2>
            <p style="color: #333; font-size: 1.1rem;">Speak your answer now</p>
            <p style="color: #666; margin: 10px 0 0 0;">Click "STOP & TRANSCRIBE" when done</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-transcribe script
        st.markdown("""
        <script>
        if (!window.speechRecognition && !window.webkitSpeechRecognition) {
            console.log("Speech recognition not supported");
        } else {
            window.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            window.recognition.continuous = true;
            window.recognition.interimResults = true;
            window.recognition.lang = 'en-US';
            window.finalTranscript = '';
            
            window.recognition.onresult = function(event) {
                let interim = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        window.finalTranscript += event.results[i][0].transcript + ' ';
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }
                if (window.finalTranscript) {
                    localStorage.setItem('voiceAnswer', window.finalTranscript);
                }
            };
            
            window.recognition.onerror = function(e) {
                console.log('Speech error:', e.error);
            };
            
            try {
                window.recognition.start();
                console.log("Speech recognition started");
            } catch(e) {
                console.log("Could not start:", e);
            }
        }
        </script>
        """, unsafe_allow_html=True)
    else:
        # Stop recognition
        st.markdown("""
        <script>
        if (window.recognition) {
            try {
                window.recognition.stop();
                console.log("Stopped, transcript:", window.finalTranscript);
                if (window.finalTranscript) {
                    localStorage.setItem('voiceAnswer', window.finalTranscript);
                }
            } catch(e) {}
        }
        </script>
        """, unsafe_allow_html=True)
    
    # Answer Input Area
    st.markdown("### ✍️ Type or Paste Your Answer")
    st.markdown("*After speaking, type or paste your answer here*")
    
    voice_answer = st.text_area(
        "Your answer...",
        value=st.session_state.get('voice_answer_text', ''),
        height=150,
        key="voice_answer",
        placeholder="Type your answer here or speak into the microphone..."
    )
    
    # Update session
    st.session_state.voice_answer_text = voice_answer
    
    # Submit buttons
    col_sub1, col_sub2, col_sub3 = st.columns([1, 1, 1])
    
    with col_sub1:
        if st.button("✅ SUBMIT ANSWER", use_container_width=True, type="primary"):
            if voice_answer.strip():
                submit_voice_answer(voice_answer)
            else:
                st.warning("Please enter or speak your answer first!")
    
    with col_sub2:
        if st.button("⏭️ SKIP", use_container_width=True):
            skip_question()
    
    with col_sub3:
        if st.button("🗣️ REPLAY QUESTION", use_container_width=True):
            try:
                voice = VoiceOutput()
                audio_file = voice.generate_question_speech(
                    current_idx + 1,
                    current_q.question_text,
                    current_q.category,
                    current_q.difficulty
                )
                if audio_file:
                    st.audio(str(audio_file), format="audio/mp3", start_time=0)
            except Exception as e:
                st.warning(f"Could not play audio: {e}")

def submit_voice_answer(answer: str):
    """Submit the voice/text answer for evaluation."""
    if not answer.strip() or not st.session_state.questions:
        return
    
    current_idx = st.session_state.question_index
    current_q = st.session_state.questions[current_idx]
    
    with st.spinner("Evaluating your answer..."):
        try:
            evaluator = AnswerEvaluator()
            evaluation = evaluator.evaluate(
                {
                    'question_text': current_q.question_text,
                    'category': current_q.category,
                    'difficulty': current_q.difficulty,
                    'topic': current_q.topic
                },
                answer
            )
            
            # Save answer
            st.session_state.answers.append({
                'question': current_q.question_text,
                'answer': answer,
                'category': current_q.category,
                'evaluation': evaluation
            })
            
            # Show feedback
            st.success("✅ Answer submitted!")
            st.balloons()
            
            # Move to next question
            st.session_state.question_index += 1
            st.session_state.voice_answer_text = ""
            st.session_state.is_listening = False
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error evaluating answer: {e}")

def skip_question():
    """Skip current question."""
    st.session_state.question_index += 1
    st.session_state.voice_answer_text = ""
    st.session_state.is_listening = False
    st.rerun()


def start_new_interview(company_mode: str, num_questions: int = None):
    """Start a new interview session."""
    session_id = str(uuid.uuid4())
    
    if num_questions is None:
        num_questions = config.interview_config.max_questions
    
    # Generate questions
    with st.spinner("Generating interview questions..."):
        try:
            generator = QuestionGenerator()
            questions = generator.generate_questions(
                st.session_state.resume_data,
                company_mode,
                count=num_questions
            )
            
            st.session_state.questions = questions
            st.session_state.question_index = 0
            st.session_state.answers = []
            st.session_state.transcript = ''
            
            # Create interview in database
            interview_id = db.create_interview(
                st.session_state.user_id,
                st.session_state.resume_id,
                company_mode
            )
            
            # Save questions to database
            for q in questions[:10]:  # Save first 10 initially
                db.save_question(
                    interview_id,
                    q.question_number,
                    q.category,
                    q.question_text,
                    q.difficulty
                )
            
            # Create memory session
            memory = create_interview_memory(
                session_id,
                st.session_state.user_id,
                st.session_state.resume_data,
                company_mode
            )
            
            st.session_state.interview_session_id = session_id
            st.session_state.interview_memory = memory
            
            db.update_interview_status(interview_id, 'in_progress')
            
            st.success("Interview started! Good luck!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to start interview: {e}")


def render_interview_controls():
    """Render interview UI controls."""
    memory = st.session_state.interview_memory
    
    if not memory or not st.session_state.questions:
        return
    
    # Progress bar
    progress = memory.progress_percentage
    st.markdown("---")
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 15px 0;">
        <h4 style="color: #333; margin: 0;">📊 Interview Progress: {int(progress)}%</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress, text=f"Question {st.session_state.question_index + 1} of {len(st.session_state.questions)}")
    
    # Current question
    current_idx = st.session_state.question_index
    questions = st.session_state.questions
    
    if current_idx >= len(questions):
        complete_interview()
        return
    
    current_question = questions[current_idx]
    
    # Question display
    render_question_box(
        current_question.question_text,
        current_question.category,
        current_question.difficulty
    )
    
    # Voice output - Auto speak when voice is enabled
    if st.session_state.voice_enabled:
        # Track which question has been spoken
        spoken_key = f"spoken_q_{current_idx}"
        
        if not st.session_state.get(spoken_key, False):
            # Auto-speak the question when displayed
            with st.spinner("🔊 Speaking..."):
                try:
                    voice = VoiceOutput()
                    voice.generate_question_speech(
                        current_idx + 1,
                        current_question.question_text,
                        current_question.category,
                        current_question.difficulty
                    )
                    st.session_state[spoken_key] = True
                    st.rerun()
                except Exception as e:
                    st.warning("Voice not available. Please type your answer.")
        
        # Show manual speak button as well
        if st.button("🔊 Replay Question", use_container_width=True):
            with st.spinner("🔊 Speaking..."):
                try:
                    voice = VoiceOutput()
                    voice.generate_question_speech(
                        current_idx + 1,
                        current_question.question_text,
                        current_question.category,
                        current_question.difficulty
                    )
                except Exception as e:
                    st.warning("Voice not available.")
    
    # Voice Recording Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b22, #feca5722); padding: 25px; border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 20px 0; border: 3px solid #ff6b6b;">
        <h3 style="color: #1a1a2e; margin: 0 0 15px 0; text-align: center;">🎤 Voice Answer Recording</h3>
        <p style="color: #666; text-align: center; margin-bottom: 20px;">Click START, speak your answer, then click STOP to transcribe and analyze</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize recording state
    if 'voice_recording' not in st.session_state:
        st.session_state.voice_recording = False
    if 'voice_transcript' not in st.session_state:
        st.session_state.voice_transcript = ""
    
    # Voice Recording Buttons
    col_rec1, col_rec2, col_rec3 = st.columns([1, 1, 1])
    
    with col_rec1:
        st.markdown("###")
        if st.button("🔴 START VOICE RECORDING", key="start_voice", use_container_width=True):
            st.session_state.voice_recording = True
            st.session_state.voice_transcript = ""
            st.rerun()
    
    with col_rec2:
        st.markdown("###")
        if st.button("⏹️ STOP & TRANSCRIBE", key="stop_voice", use_container_width=True):
            st.session_state.voice_recording = False
            st.rerun()
    
    with col_rec3:
        st.markdown("###")
        if st.button("🔄 CLEAR", key="clear_voice", use_container_width=True):
            st.session_state.voice_recording = False
            st.session_state.voice_transcript = ""
            st.rerun()
    
    # Recording indicator
    if st.session_state.voice_recording:
        st.markdown("""
        <div style="background: rgba(235, 51, 73, 0.15); padding: 30px; border-radius: 16px; text-align: center; margin: 20px 0; border: 3px solid #eb3349;">
            <span style="font-size: 4rem; animation: pulse 1s infinite; display: inline-block;">🔴</span>
            <h2 style="color: #eb3349; margin: 15px 0 5px 0;">🎙️ LISTENING...</h2>
            <p style="color: #333; margin: 0; font-size: 1.1rem;">Speak your answer clearly into the microphone</p>
            <p style="color: #666; margin: 15px 0 0 0;">💡 Tip: Speak naturally and answer the question fully</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add audio recording script that starts speech recognition
        st.markdown("""
        <script>
        // Auto-start speech recognition when recording starts
        setTimeout(function() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                window.recognition = new SpeechRecognition();
                window.recognition.continuous = true;
                window.recognition.interimResults = true;
                window.recognition.lang = 'en-US';
                window.finalTranscript = '';
                
                window.recognition.onresult = function(event) {
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        if (event.results[i].isFinal) {
                            window.finalTranscript += event.results[i][0].transcript + ' ';
                        }
                    }
                };
                
                window.recognition.onerror = function(event) {
                    console.log('Speech recognition error:', event.error);
                };
                
                try {
                    window.recognition.start();
                    console.log('Speech recognition started');
                } catch(e) {
                    console.log('Could not start recognition:', e);
                }
            }
        }, 500);
        </script>
        """, unsafe_allow_html=True)
    else:
        # Stop speech recognition when not recording
        st.markdown("""
        <script>
        setTimeout(function() {
            if (window.recognition) {
                try {
                    window.recognition.stop();
                    console.log('Speech recognition stopped, transcript:', window.finalTranscript);
                    // Store final transcript
                    if (window.finalTranscript) {
                        window.localStorage.setItem('lastTranscript', window.finalTranscript.trim());
                    }
                } catch(e) {
                    console.log('Could not stop recognition:', e);
                }
            }
        }, 500);
        </script>
        """, unsafe_allow_html=True)
    
    # Embedded Voice Recorder with Live Transcript
    st.markdown("""
    <div style="background: linear-gradient(135deg, #48dbfb22, #0abde322); padding: 20px; border-radius: 16px; margin: 20px 0; border: 2px solid #48dbfb;">
        <h4 style="color: #1a1a2e; margin: 0 0 10px 0;">🎙️ Voice Recorder</h4>
        <p style="color: #666; margin: 0 0 15px 0;">Use the buttons above to record your voice answer</p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
            <p style="color: #888; margin: 0; font-size: 0.9rem;">📋 Your transcript will appear here after you speak</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Manual text input for transcribed answer
    st.markdown("""
    <div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 20px 0;">
        <h4 style="color: #333; margin: 0 0 10px 0;">📝 Your Spoken Answer</h4>
        <p style="color: #888; margin: 0 0 15px 0; font-size: 0.9rem;">Type or paste your spoken answer here after recording</p>
    </div>
    """, unsafe_allow_html=True)
    
    voice_answer = st.text_area(
        "Speak your answer, then type or paste it here...",
        value=st.session_state.voice_transcript,
        height=150,
        key="voice_answer_input",
        placeholder="After speaking your answer, type or paste it here for analysis..."
    )
    
    col_voice_submit, col_voice_skip = st.columns([1, 1])
    
    with col_voice_submit:
        if st.button("✅ SUBMIT VOICE ANSWER", key="submit_voice", use_container_width=True, type="primary"):
            if voice_answer:
                process_answer(voice_answer)
                st.session_state.voice_transcript = ""
                st.success("✅ Answer submitted for analysis!")
            else:
                st.warning("⚠️ Please enter or speak your answer first!")
    
    with col_voice_skip:
        if st.button("⏭️ SKIP QUESTION", key="skip_voice", use_container_width=True):
            skip_question()
    
    st.markdown("---")
    
    # Alternative: Type Answer Section
    st.markdown("""
    <div style="background: rgba(255,255,255,0.95); padding: 25px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 20px 0;">
        <h4 style="color: #333; margin: 0 0 15px 0;">✍️ Or Type Your Answer</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        typed_answer = st.text_area(
            "Type your answer here...",
            height=150,
            key="typed_answer",
            placeholder="Enter your answer to the question..."
        )
    
    with col2:
        st.markdown("###")
        if st.button("✅ Submit Typed Answer", use_container_width=True, type="primary"):
            if typed_answer:
                process_answer(typed_answer)
            else:
                st.warning("⚠️ Please enter an answer!")
    
    with col3:
        st.markdown("###")
        if st.button("⏭️ Skip Question", use_container_width=True):
            skip_question()
    
    # Previous answer feedback
    if st.session_state.answers and current_idx > 0:
        prev_answer = st.session_state.answers[-1]
        if prev_answer.get('evaluation'):
            show_answer_feedback(prev_answer)


def start_recording():
    """Start audio recording."""
    st.session_state.is_recording = True
    st.session_state.transcript = ''
    st.rerun()


def stop_recording():
    """Stop recording and process audio."""
    st.session_state.is_recording = False
    
    # In a real implementation, this would capture actual audio
    # For now, we'll use a placeholder
    st.session_state.transcript = "Sample transcribed answer..."
    
    st.rerun()


def process_answer(answer: str):
    """Process and evaluate the answer."""
    if not answer or not st.session_state.questions:
        return
    
    current_question = st.session_state.questions[st.session_state.question_index]
    
    # Evaluate answer
    with st.spinner("Evaluating your answer..."):
        try:
            evaluator = AnswerEvaluator()
            evaluation = evaluator.evaluate(
                {
                    'question_text': current_question.question_text,
                    'category': current_question.category,
                    'difficulty': current_question.difficulty
                },
                answer,
                st.session_state.resume_data
            )
            
            # Store answer
            answer_data = {
                'question_id': current_question.id,
                'question': current_question.question_text,
                'category': current_question.category,
                'answer': answer,
                'score': evaluation.overall_score,
                'evaluation': evaluator.to_dict(evaluation)
            }
            
            st.session_state.answers.append(answer_data)
            
            # Update memory
            if st.session_state.interview_memory:
                memory_manager.add_answer(
                    st.session_state.interview_session_id,
                    current_question.id,
                    answer,
                    evaluation.overall_score,
                    evaluator.to_dict(evaluation)
                )
            
            # Move to next question
            st.session_state.question_index += 1
            st.session_state.transcript = ''
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing answer: {e}")


def skip_question():
    """Skip the current question."""
    st.session_state.question_index += 1
    st.session_state.transcript = ''
    st.rerun()


def show_answer_feedback(answer_data: Dict):
    """Display feedback for the previous answer."""
    evaluation = answer_data.get('evaluation', {})
    
    st.markdown("### 📊 Last Answer Feedback")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = answer_data.get('score', 0)
        color = "green" if score >= 7 else ("orange" if score >= 5 else "red")
        st.markdown(f"**Score:** :{color}[{score}/10]")
    
    with col2:
        strengths = evaluation.get('strengths', [])
        if strengths:
            st.markdown(f"**Strengths:** {', '.join(strengths[:2])}")
    
    with col3:
        weaknesses = evaluation.get('weaknesses', [])
        if weaknesses:
            st.markdown(f"**Areas to Improve:** {', '.join(weaknesses[:2])}")
    
    # Improvement tips
    tips = evaluation.get('improvement_tips', [])
    if tips:
        with st.expander("💡 Improvement Tips"):
            for tip in tips:
                st.markdown(f"- {tip}")


def complete_interview():
    """Complete the interview and generate report."""
    st.markdown("## 🎉 Interview Complete!")
    
    # Calculate category scores
    category_scores = {}
    for answer in st.session_state.answers:
        cat = answer.get('category', 'other')
        score = answer.get('score', 0)
        if score > 0:
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(score)
    
    avg_scores = {
        cat: round(sum(scores) / len(scores), 2)
        for cat, scores in category_scores.items()
    }
    
    # Generate report
    with st.spinner("Generating report..."):
        try:
            report_gen = ReportGenerator()
            report = report_gen.generate_report(
                st.session_state.interview_memory.to_dict(),
                st.session_state.resume_data,
                avg_scores
            )
            
            # Display report summary
            st.markdown(f"""
            ### 📊 Interview Summary
            
            **Candidate:** {report.candidate_name}
            **Overall Score:** {report.overall_score}/10
            **Interview Readiness:** {report.interview_readiness}%
            
            ### Hiring Recommendation: **{report.hiring_recommendation}**
            """)
            
            # Score breakdown chart
            if avg_scores:
                fig = px.bar(
                    x=list(avg_scores.keys()),
                    y=list(avg_scores.values()),
                    labels={'x': 'Category', 'y': 'Score'},
                    title="Score by Category"
                )
                st.plotly_chart(fig)
            
            # Generate PDF
            pdf_path = report_gen.export_pdf(report)
            if pdf_path:
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        "📥 Download Report (PDF)",
                        f,
                        file_name=f"interview_report_{report.session_id}.pdf"
                    )
            
            # Reset for new interview
            if st.button("🔄 Start New Interview"):
                reset_interview_state()
                
        except Exception as e:
            st.error(f"Error generating report: {e}")


def reset_interview_state():
    """Reset interview state for a new session."""
    st.session_state.interview_session_id = None
    st.session_state.interview_memory = None
    st.session_state.questions = []
    st.session_state.question_index = 0
    st.session_state.answers = []
    st.session_state.transcript = ''
    st.session_state.is_recording = False
    st.rerun()


# ==================== HISTORY PAGE ====================

def history_page():
    """Interview history page."""
    st.markdown("# 📝 Interview History")
    
    interviews = db.get_user_interviews(st.session_state.user_id)
    
    if not interviews:
        st.info("No interviews completed yet.")
        return
    
    for interview in interviews:
        with st.expander(f"📋 Interview - {interview['created_at'][:10]} | Score: {interview.get('overall_score', 'N/A')}"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**Company Mode:** {interview['company_mode']}")
                st.markdown(f"**Status:** {interview['status']}")
                st.markdown(f"**Questions:** {interview.get('total_questions', 'N/A')}")
            
            with col2:
                if interview.get('overall_score'):
                    st.metric("Overall Score", f"{interview['overall_score']}/10")
                
                if st.button("View Details", key=f"view_{interview['id']}"):
                    show_interview_details(interview['id'])


def show_interview_details(interview_id: int):
    """Show detailed interview results."""
    # Get questions and answers
    questions = db.get_interview_questions(interview_id)
    answers = db.get_interview_answers(interview_id)
    
    st.markdown("### Questions & Answers")
    
    for i, q in enumerate(questions):
        with st.expander(f"Q{i+1}: {q['question_text'][:50]}..."):
            st.markdown(f"**Category:** {q['category']}")
            st.markdown(f"**Difficulty:** {q['difficulty']}")
            
            # Find answer
            answer = next((a for a in answers if a['question_id'] == q['id']), None)
            if answer:
                if answer.get('answer_text'):
                    st.markdown(f"**Your Answer:** {answer['answer_text']}")
                if answer.get('score'):
                    st.metric("Score", f"{answer['score']}/10")


# ==================== SETTINGS PAGE ====================

def settings_page():
    """Settings page."""
    st.markdown("# ⚙️ Settings")
    
    # Voice settings
    st.markdown("### 🎤 Voice Settings")
    
    voice_options = {
        'en-US-AriaNeural': 'Aria (American Female)',
        'en-US-JennyNeural': 'Jenny (American Female)',
        'en-US-GuyNeural': 'Guy (American Male)',
        'en-IN-NeerjaExpressive': 'Neerja (Indian Female)',
        'en-IN-PrabhatNeural': 'Prabhat (Indian Male)'
    }
    
    selected_voice = st.selectbox(
        "Interviewer Voice",
        options=list(voice_options.keys()),
        format_func=lambda x: voice_options[x],
        index=0
    )
    
    st.session_state.selected_voice = selected_voice
    
    # Voice rate
    rate = st.slider("Speech Rate", -50, 50, 0, help="Adjust how fast the interviewer speaks")
    
    # Voice pitch
    pitch = st.slider("Voice Pitch", -20, 20, 0, help="Adjust the pitch of the voice")
    
    # Profile settings
    st.markdown("---")
    st.markdown("### 👤 Profile Settings")
    
    profile = db.get_user_profile(st.session_state.user_id)
    
    with st.form("profile_form"):
        full_name = st.text_input("Full Name", value=profile.get('full_name', '') if profile else '')
        phone = st.text_input("Phone", value=profile.get('phone', '') if profile else '')
        linkedin = st.text_input("LinkedIn URL", value=profile.get('linkedin_url', '') if profile else '')
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            db.update_user_profile(st.session_state.user_id, {
                'full_name': full_name,
                'phone': phone,
                'linkedin_url': linkedin
            })
            st.success("Profile updated!")


# ==================== MAIN ====================

def main():
    """Main application entry point."""
    init_session_state()
    
    if not st.session_state.logged_in:
        auth_page()
        return
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    page = st.session_state.current_page
    
    if page == "home":
        home_page()
    elif page == "resume":
        resume_page()
    elif page == "dashboard":
        dashboard_page()
    elif page == "interview":
        interview_page()
    elif page == "history":
        history_page()
    elif page == "settings":
        settings_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
