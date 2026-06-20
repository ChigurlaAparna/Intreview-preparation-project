"""
AI Interview Preparation App
Powered by Google Gemini API
"""

import streamlit as st
import os
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Interview Prep | Master Your Next Interview",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --dark: #0f172a;
        --light: #f8fafc;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #6366f1 !important;
    }
    
    /* Cards */
    .stCard {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #334155;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 16px 20px;
        margin: 8px 0;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #f1f5f9;
        border-radius: 18px 18px 18px 4px;
        padding: 16px 20px;
        margin: 8px 0;
        border: 1px solid #475569;
    }
    
    /* Mode buttons */
    .mode-btn {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border: none;
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    /* Stats */
    .stat-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid #334155;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #6366f1;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Technical Interview"

if 'session_stats' not in st.session_state:
    st.session_state.session_stats = {
        'questions_answered': 0,
        'questions_asked': 0,
        'session_time': 0
    }

if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""

if 'job_description' not in st.session_state:
    st.session_state.job_description = ""

# Interview modes configuration
INTERVIEW_MODES = {
    "Technical Interview": {
        "icon": "💻",
        "description": "Practice coding questions, system design, and technical concepts",
        "topics": ["Python", "Data Structures", "Algorithms", "Machine Learning", "System Design", "Databases"]
    },
    "Behavioral Interview": {
        "icon": "🎯",
        "description": "Master STAR method responses to behavioral questions",
        "topics": ["Leadership", "Teamwork", "Problem Solving", "Communication", "Adaptability"]
    },
    "Resume Review": {
        "icon": "📄",
        "description": "Get feedback on your resume and suggestions for improvement",
        "topics": ["Format", "Content", "Achievements", "Keywords", "Quantification"]
    },
    "Mock Interview": {
        "icon": "🎭",
        "description": "Full simulated interview with random questions from all categories",
        "topics": ["Technical", "Behavioral", "Situational", "Case Studies"]
    },
    "Custom Practice": {
        "icon": "⚙️",
        "description": "Create your own interview focus based on specific requirements",
        "topics": ["Custom"]
    }
}

# Technical questions database
TECHNICAL_QUESTIONS = {
    "Python": [
        "Explain the difference between a list and a tuple in Python.",
        "What are Python decorators and how would you create one?",
        "How does Python's garbage collection work?",
        "Explain the GIL (Global Interpreter Lock) in Python.",
        "What is the difference between deep copy and shallow copy?",
        "How would you handle exceptions in Python?",
        "Explain list comprehensions and provide an example.",
        "What are *args and **kwargs?",
        "How does Python's memory management work?",
        "Explain the difference between @staticmethod and @classmethod."
    ],
    "Data Structures": [
        "What is the time complexity of accessing an element in an array?",
        "Explain the difference between a stack and a queue.",
        "How would you implement a binary search tree?",
        "What is a hash table and how does it handle collisions?",
        "Explain the difference between BFS and DFS.",
        "What is a linked list and when would you use it over an array?",
        "How does a heap data structure work?",
        "What is a Trie and what are its applications?",
        "Explain the concept of graph traversal.",
        "What is the difference between a directed and undirected graph?"
    ],
    "Algorithms": [
        "Explain the time complexity of quicksort.",
        "How would you find the shortest path in a weighted graph?",
        "What is dynamic programming and when would you use it?",
        "Explain the divide and conquer approach.",
        "How does binary search work?",
        "What is the difference between greedy algorithms and dynamic programming?",
        "Explain merge sort and its time complexity.",
        "How would you detect a cycle in a linked list?",
        "What is backtracking and when is it used?",
        "Explain the concept of recursion and its pros/cons."
    ],
    "Machine Learning": [
        "What is the difference between supervised and unsupervised learning?",
        "Explain overfitting and how to prevent it.",
        "What is the bias-variance tradeoff?",
        "How does gradient descent work?",
        "Explain the difference between L1 and L2 regularization.",
        "What are the assumptions of linear regression?",
        "How would you handle imbalanced datasets?",
        "Explain the working of Random Forest.",
        "What is cross-validation and why is it important?",
        "How does backpropagation work in neural networks?"
    ],
    "System Design": [
        "How would you design a URL shortening service like Bitly?",
        "Design a chat application like WhatsApp.",
        "How would you scale a web application to handle millions of users?",
        "Design a rate limiter for an API.",
        "How would you design a search autocomplete feature?",
        "Design a distributed cache system.",
        "How would you design Twitter's newsfeed?",
        "Design an elevator system.",
        "How would you design a video streaming service like Netflix?",
        "Design a URL monitoring service."
    ],
    "Databases": [
        "What is the difference between SQL and NoSQL databases?",
        "Explain ACID properties in databases.",
        "What is database normalization and why is it important?",
        "How does indexing improve query performance?",
        "What is the difference between clustered and non-clustered indexes?",
        "Explain database transactions and their isolation levels.",
        "What is sharding and when would you use it?",
        "How would you optimize a slow-running SQL query?",
        "What is a foreign key and why is it used?",
        "Explain the CAP theorem."
    ]
}

# Behavioral questions database
BEHAVIORAL_QUESTIONS = [
    {"question": "Tell me about a time when you had to work under pressure.", "category": "Stress Management"},
    {"question": "Describe a situation where you had to deal with a difficult team member.", "category": "Teamwork"},
    {"question": "Give an example of a goal you reached and how you achieved it.", "category": "Goal Setting"},
    {"question": "Tell me about a time you made a mistake. How did you handle it?", "category": "Accountability"},
    {"question": "Describe a situation where you had to adapt to a major change.", "category": "Adaptability"},
    {"question": "Tell me about a time you led a team through a challenging project.", "category": "Leadership"},
    {"question": "Describe a situation where you had to convince others to see your point of view.", "category": "Persuasion"},
    {"question": "Give an example of when you used data to make a decision.", "category": "Data-Driven"},
    {"question": "Tell me about a time you failed and what you learned from it.", "category": "Learning"},
    {"question": "Describe your approach to handling conflicting priorities.", "category": "Time Management"}
]

def get_gemini_response(prompt: str, api_key: str) -> str:
    """Get response from Gemini API"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_technical_question(topic: str, difficulty: str = "medium") -> str:
    """Generate a technical question based on topic and difficulty"""
    questions = TECHNICAL_QUESTIONS.get(topic, TECHNICAL_QUESTIONS["Python"])
    import random
    return random.choice(questions)

def generate_behavioral_question() -> dict:
    """Get a random behavioral question"""
    import random
    return random.choice(BEHAVIORAL_QUESTIONS)

def evaluate_answer(question: str, answer: str, rubric: dict) -> dict:
    """Evaluate the user's answer and provide feedback"""
    evaluation_prompt = f"""You are an expert interview coach. Evaluate the following interview response.

Interview Question: {question}

Candidate's Answer: {answer}

Provide a detailed evaluation with:
1. Overall Score (1-10)
2. Strengths (bullet points)
3. Areas for Improvement (bullet points)
4. Suggested Answer Structure
5. Tips for Better Response

Format your response in a clear, structured manner."""

    api_key = os.environ.get('GEMINI_API_KEY', '')
    if api_key:
        response = get_gemini_response(evaluation_prompt, api_key)
        return {"feedback": response, "score": "AI Evaluated"}
    else:
        return {
            "feedback": "Demo mode: Add your Gemini API key to get AI-powered feedback.",
            "score": "Demo"
        }

def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Analyze resume against job description"""
    analysis_prompt = f"""You are an expert resume reviewer. Analyze the following resume against the job description.

Job Description:
{job_description}

Resume Content:
{resume_text}

Provide:
1. Match Score (1-10)
2. Missing Keywords/Skills
3. Strengths in the Resume
4. Areas for Improvement
5. ATS Optimization Tips
6. Suggested Changes

Format as a detailed report."""

    api_key = os.environ.get('GEMINI_API_KEY', '')
    if api_key:
        response = get_gemini_response(analysis_prompt, api_key)
        return {"analysis": response, "score": "AI Analyzed"}
    else:
        return {
            "analysis": "Demo mode: Add your Gemini API key to get AI-powered resume analysis.",
            "score": "Demo"
        }

def generate_mock_interview_questions(count: int = 5) -> list:
    """Generate a mix of interview questions for mock interview"""
    questions = []
    
    # Add technical questions
    for _ in range(count // 3):
        topic = import_random.choice(list(TECHNICAL_QUESTIONS.keys()))
        questions.append({
            "type": "technical",
            "topic": topic,
            "question": generate_technical_question(topic)
        })
    
    # Add behavioral questions
    for _ in range(count - len(questions)):
        q = generate_behavioral_question()
        questions.append({
            "type": "behavioral",
            "category": q["category"],
            "question": q["question"]
        })
    
    import random
    random.shuffle(questions)
    return questions

# Import at module level
import random as import_random

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 AI Interview Prep")
    st.markdown("---")
    
    # API Key input
    st.markdown("#### 🔑 API Configuration")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get your free API key from Google AI Studio",
        placeholder="AIza..."
    )
    if api_key:
        os.environ['GEMINI_API_KEY'] = api_key
        st.success("✅ API Key configured!")
    
    st.markdown("---")
    
    # Session stats
    st.markdown("#### 📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Questions", st.session_state.session_stats['questions_answered'])
    with col2:
        st.metric("Asked", st.session_state.session_stats['questions_asked'])
    
    st.markdown("---")
    
    # Interview mode selection
    st.markdown("#### 🎯 Select Interview Mode")
    mode = st.selectbox(
        "Choose your focus",
        options=list(INTERVIEW_MODES.keys()),
        format_func=lambda x: f"{INTERVIEW_MODES[x]['icon']} {x}"
    )
    
    if st.button("🚀 Start Interview", use_container_width=True):
        st.session_state.current_mode = mode
        st.session_state.conversation_history = []
        st.rerun()
    
    st.markdown("---")
    
    # Tips section
    st.markdown("#### 💡 Pro Tips")
    st.info("""
    • Use STAR method for behavioral questions
    • Practice out loud, not just in your head
    • Take notes during the interview
    • Ask clarifying questions
    """)
    
    st.markdown("---")
    st.markdown("*Powered by Google Gemini AI*")

# Main content
st.title("🎯 AI Interview Preparation")
st.markdown("*Master your next interview with AI-powered practice*")

# Mode display
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode_info = INTERVIEW_MODES.get(st.session_state.current_mode, INTERVIEW_MODES["Technical Interview"])
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; border: 1px solid #334155;">
        <h2 style="margin: 0;">{mode_info['icon']} {st.session_state.current_mode}</h2>
        <p style="color: #94a3b8; margin-top: 10px;">{mode_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["📝 Practice Mode", "📄 Resume Review", "📚 Question Bank", "🎯 Mock Interview"])

# Tab 1: Practice Mode
with tab1:
    st.header("📝 Interactive Practice")
    
    if st.session_state.current_mode == "Technical Interview":
        col1, col2 = st.columns([1, 1])
        with col1:
            topic = st.selectbox("Select Topic", options=list(TECHNICAL_QUESTIONS.keys()))
        with col2:
            difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard", "Expert"])
        
        if st.button("🎲 Get New Question"):
            question = generate_technical_question(topic, difficulty.lower())
            st.session_state.conversation_history.append({"role": "assistant", "content": question})
            st.session_state.session_stats['questions_asked'] += 1
            st.rerun()
        
        # Show topic overview
        st.markdown("#### 📚 Topic Overview")
        topic_expander = st.expander(f"View {topic} key concepts")
        topic_concepts = {
            "Python": "Variables, Functions, Classes, Decorators, Generators, Context Managers, Lambda, Comprehensions",
            "Data Structures": "Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables, Heaps",
            "Algorithms": "Sorting, Searching, Recursion, Dynamic Programming, Greedy, Divide & Conquer",
            "Machine Learning": "Supervised/Unsupervised Learning, Neural Networks, Feature Engineering, Model Evaluation",
            "System Design": "Scalability, Load Balancing, Caching, Database Sharding, Microservices",
            "Databases": "SQL, NoSQL, Indexing, Transactions, ACID, Normalization, Replication"
        }
        topic_expander.markdown(f"**Key Concepts:**\n\n{topic_concepts.get(topic, 'General programming concepts')}")
    
    elif st.session_state.current_mode == "Behavioral Interview":
        st.markdown("##### Using the STAR Method:")
        st.info("""
        **S** - Situation: Set the context
        **T** - Task: Describe your responsibility  
        **A** - Action: Explain what you did
        **R** - Result: Share the outcome
        """)
        
        if st.button("🎯 Get Behavioral Question"):
            q = generate_behavioral_question()
            st.session_state.conversation_history.append({
                "role": "assistant", 
                "content": f"**Category: {q['category']}**\n\n{q['question']}"
            })
            st.session_state.session_stats['questions_asked'] += 1
            st.rerun()
    
    elif st.session_state.current_mode == "Mock Interview":
        st.markdown("##### 🎭 Full Mock Interview")
        st.markdown("Practice with a mix of technical and behavioral questions")
        
        num_questions = st.slider("Number of Questions", 3, 10, 5)
        
        if st.button("🎬 Start Mock Interview", use_container_width=True):
            questions = generate_mock_interview_questions(num_questions)
            st.session_state.conversation_history = [{"role": "assistant", "content": "🎬 Mock Interview Started!\n\nYou'll be asked a mix of questions. Take your time and answer as if in a real interview.\n\n---"}]
            for i, q in enumerate(questions, 1):
                q_type = q['type'].upper()
                if q['type'] == 'technical':
                    content = f"**[{q_type}] {q['topic']}**\n\n{q['question']}"
                else:
                    content = f"**[{q_type}] {q['category']}**\n\n{q['question']}"
                st.session_state.conversation_history.append({"role": "assistant", "content": content})
            st.session_state.session_stats['questions_asked'] += num_questions
            st.rerun()
    
    elif st.session_state.current_mode == "Custom Practice":
        st.markdown("##### ⚙️ Custom Interview Setup")
        
        custom_topics = st.multiselect(
            "Select Topics",
            options=["Python", "Machine Learning", "System Design", "Behavioral", "Leadership", "Communication"],
            default=["Python"]
        )
        
        custom_difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced", "Expert"])
        
        question_style = st.radio("Question Style", ["Direct", "Case Study", "Scenario-based", "Real-world Application"])
        
        if st.button("⚡ Generate Custom Questions"):
            st.info(f"Custom practice configured for: {', '.join(custom_topics)} at {custom_difficulty} level")
    
    # Chat interface
    st.markdown("---")
    st.subheader("💬 Interview Chat")
    
    # Display conversation
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.conversation_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">👤 You: {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">🤖 Question: {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Answer input
    st.markdown("#### ✍️ Your Answer:")
    answer = st.text_area("", height=150, placeholder="Type your answer here...", key="answer_input")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit = st.button("📤 Submit Answer", use_container_width=True)
    
    if submit and answer:
        st.session_state.conversation_history.append({"role": "user", "content": answer})
        st.session_state.session_stats['questions_answered'] += 1
        
        # Get evaluation
        if st.session_state.conversation_history:
            last_question = ""
            for msg in reversed(st.session_state.conversation_history[:-1]):
                if msg["role"] == "assistant":
                    last_question = msg["content"]
                    break
            
            if last_question and os.environ.get('GEMINI_API_KEY'):
                with st.spinner("🤔 Evaluating your answer..."):
                    evaluation = evaluate_answer(last_question, answer, {})
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": f"📊 **Evaluation:**\n\n{evaluation['feedback']}"
                    })
            else:
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": "💡 **Tips for improvement:**\n\n• Be more specific with examples\n• Quantify your achievements\n• Structure your answer clearly\n• Practice the STAR method"
                })
        
        st.rerun()
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.conversation_history = []
        st.rerun()

# Tab 2: Resume Review
with tab2:
    st.header("📄 Resume Review & Analysis")
    st.markdown("*Get AI-powered feedback on your resume*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📝 Paste Your Resume")
        resume_input = st.text_area(
            "",
            height=300,
            placeholder="Paste your resume text here...",
            key="resume_input"
        )
        
        if resume_input:
            st.session_state.resume_text = resume_input
        
        if st.button("📤 Upload Resume File", use_container_width=True):
            st.info("File upload coming soon! For now, paste your resume text above.")
    
    with col2:
        st.markdown("#### 💼 Job Description (Optional)")
        job_input = st.text_area(
            "",
            height=300,
            placeholder="Paste the job description here for ATS analysis...",
            key="job_input"
        )
        
        if job_input:
            st.session_state.job_description = job_input
    
    st.markdown("---")
    
    if st.button("🔍 Analyze Resume", use_container_width=True):
        if st.session_state.resume_text or resume_input:
            with st.spinner("🤖 Analyzing your resume..."):
                resume_text = resume_input or st.session_state.resume_text
                job_desc = job_input or st.session_state.job_description
                
                analysis = analyze_resume(resume_text, job_desc)
                
                st.markdown("#### 📊 Analysis Results")
                st.info(analysis["analysis"])
        else:
            st.warning("⚠️ Please paste your resume text above first!")

# Tab 3: Question Bank
with tab3:
    st.header("📚 Question Bank")
    
    category = st.selectbox("Select Category", ["All"] + list(TECHNICAL_QUESTIONS.keys()) + ["Behavioral"])
    
    if category == "All":
        st.markdown("### Technical Questions")
        for topic, questions in TECHNICAL_QUESTIONS.items():
            with st.expander(f"📁 {topic} ({len(questions)} questions)"):
                for i, q in enumerate(questions, 1):
                    st.markdown(f"**{i}.** {q}")
    
    elif category == "Behavioral":
        st.markdown("### Behavioral Questions")
        for i, q in enumerate(BEHAVIORAL_QUESTIONS, 1):
            with st.expander(f"📁 {q['category']}"):
                st.markdown(f"**Question:** {q['question']}")
    
    else:
        st.markdown(f"### {category} Questions")
        for i, q in enumerate(TECHNICAL_QUESTIONS.get(category, []), 1):
            st.markdown(f"**{i}.** {q}")

# Tab 4: Mock Interview
with tab4:
    st.header("🎯 Mock Interview Suite")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 16px; border: 1px solid #334155; margin: 20px 0;">
        <h3 style="color: #6366f1;">🎭 Experience a Real Interview</h3>
        <p style="color: #94a3b8;">Our AI-powered mock interview simulates real interview conditions with timed responses, varied question types, and comprehensive feedback.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">🎯</div>
            <h4>Technical Focus</h4>
            <p>Coding & System Design</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Technical Mock", use_container_width=True):
            st.session_state.current_mode = "Technical Interview"
            st.info("Go to Practice Mode tab to start!")
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">💼</div>
            <h4>Behavioral Focus</h4>
            <p>STAR Method Practice</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Behavioral Mock", use_container_width=True):
            st.session_state.current_mode = "Behavioral Interview"
            st.info("Go to Practice Mode tab to start!")
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">🎲</div>
            <h4>Random Mix</h4>
            <p>All Question Types</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Mixed Mock", use_container_width=True):
            st.session_state.current_mode = "Mock Interview"
            st.info("Go to Practice Mode tab to start!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 20px;">
    <p>🎯 AI Interview Prep | Powered by Google Gemini API</p>
    <p style="font-size: 0.9em;">Practice makes perfect. Start preparing today!</p>
</div>
""", unsafe_allow_html=True)
