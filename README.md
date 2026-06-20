# 🎯 AI Interview Preparation

An intelligent interview preparation platform powered by Google Gemini API.

## Features

### 📝 Practice Modes
- **Technical Interview** - Practice coding, data structures, algorithms, ML, and system design
- **Behavioral Interview** - Master the STAR method with real interview questions
- **Mock Interview** - Full simulated interviews with mixed question types
- **Resume Review** - Get AI-powered feedback on your resume
- **Custom Practice** - Create your own interview focus

### 🤖 AI Features
- Intelligent answer evaluation
- Personalized feedback and suggestions
- Resume ATS optimization
- Question generation based on difficulty

### 📚 Question Bank
- 50+ Technical questions covering:
  - Python
  - Data Structures
  - Algorithms
  - Machine Learning
  - System Design
  - Databases
- 20+ Behavioral questions
- Multiple difficulty levels

## Installation

```bash
# Clone or navigate to the project
cd interview_prep

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# Run the app
streamlit run app.py
```

## Getting Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the sidebar
4. Create a new API key
5. Copy and use it in the app

## Usage

### 1. Enter API Key
Enter your Gemini API key in the sidebar to enable AI features.

### 2. Select Interview Mode
Choose from Technical, Behavioral, Mock, or Custom practice.

### 3. Start Practicing
- Get random questions based on your selected mode
- Type your answers in the chat interface
- Submit for AI-powered evaluation
- Review feedback and improve

### 4. Resume Review
- Paste your resume
- Optionally add job description for ATS analysis
- Get detailed feedback

## Project Structure

```
interview_prep/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
├── data/              # Data files
└── src/
    ├── __init__.py
    ├── gemini_client.py    # Gemini API integration
    └── question_bank.py     # Question management
```

## Tech Stack

- **Streamlit** - Web UI framework
- **Google Gemini API** - AI-powered features
- **Python** - Core language

## License

MIT License - Feel free to use and modify!

---

Built with ❤️ for job seekers and career changers.
