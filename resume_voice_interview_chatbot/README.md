# 🎤 Resume Voice Interview Chatbot

An AI-powered voice interview preparation chatbot that simulates real interviews with personalized questions, voice interaction, and comprehensive feedback.

## 🌟 Features

### Core Functionality
- **📄 Resume Analysis** - Upload PDF/DOCX resumes and get detailed analysis
- **🎯 Personalized Questions** - AI-generated interview questions based on your profile
- **🎤 Voice Interviews** - Speak your answers and get real-time transcription
- **📊 AI Evaluation** - Instant feedback on technical accuracy, communication, and more
- **📈 Comprehensive Reports** - Detailed performance analysis with PDF export

### Supported Companies
- Service Companies: TCS, Infosys, Accenture, Deloitte, Capgemini, Cognizant
- Product Companies: Microsoft, Amazon, Google

### Question Categories
- HR & Behavioral
- Technical Knowledge
- Programming & Coding
- SQL & Databases
- Python
- Machine Learning & Deep Learning
- NLP
- Project Experience
- System Design
- OOP & Design Patterns

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or conda
- API keys (optional but recommended):
  - Google Gemini API key
  - OpenAI API key (for Whisper)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd resume_voice_interview_chatbot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
touch .env

# Add your API keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

5. Run the application:
```bash
streamlit run app.py
```

## 📁 Project Structure

```
resume_voice_interview_chatbot/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── database.py            # SQLite database operations
├── resume_parser.py       # PDF/DOCX resume parsing
├── resume_analyzer.py     # AI-powered resume analysis
├── question_generator.py  # AI question generation
├── voice_input.py         # Speech-to-text
├── voice_output.py        # Text-to-speech
├── answer_evaluator.py    # AI answer evaluation
├── memory.py              # Conversation memory
├── report_generator.py    # Report generation & PDF export
├── prompts.py             # AI prompt templates
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── uploads/               # Uploaded resumes
├── database/              # SQLite database
├── reports/               # Generated reports
└── assets/                # Static assets
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional: Override default settings
LOG_LEVEL=INFO
MAX_QUESTIONS=25
```

### Voice Settings

The application supports:
- Multiple voices (US/UK/Indian accents)
- Adjustable speech rate
- Adjustable pitch
- Auto-detection of Indian English accent

### Database

SQLite database is automatically created on first run. No additional setup required.

## 🎯 Usage Guide

### 1. Create Account & Login
- Register with username, email, and password
- Login to access the dashboard

### 2. Upload Resume
- Go to Resume Upload page
- Upload your resume (PDF or DOCX)
- Wait for AI analysis to complete
- Review extracted information and insights

### 3. Start Interview
- Select target company mode
- Enable voice if desired
- Click "Start Interview"
- Listen to questions (or read them)
- Speak or type your answers
- Receive real-time feedback

### 4. Review Results
- View overall score and category breakdown
- See strengths and areas for improvement
- Download PDF report
- Get personalized learning recommendations

## 🎤 Voice Features

### Speech-to-Text
- Uses Whisper API for accurate transcription
- Supports Indian English accent
- Automatic silence detection
- Real-time transcript display

### Text-to-Speech
- Uses Edge TTS for natural voice
- Multiple voice options
- Adjustable rate and pitch
- Professional interviewer tone

## 📊 Evaluation Criteria

Each answer is evaluated on:
1. **Technical Accuracy** (20%) - Correctness of technical content
2. **Communication** (15%) - Clarity and organization
3. **Completeness** (15%) - Thoroughness of answer
4. **Confidence** (10%) - Level of certainty
5. **Fluency** (10%) - Smooth delivery
6. **Grammar** (10%) - Language correctness
7. **Problem Solving** (10%) - Approach to problems
8. **Domain Knowledge** (10%) - Subject expertise

## 🔒 Security

- Passwords are hashed using PBKDF2 with salt
- API keys stored in environment variables
- User data stored locally in SQLite
- No data sent to third-party servers (except AI APIs)

## 📝 API Documentation

### Gemini API Integration

The application uses Google Gemini Pro for:
- Resume analysis and skill gap detection
- Question generation
- Answer evaluation
- Follow-up question generation
- Report generation

### Whisper API Integration

Used for speech-to-text transcription of voice answers.

## 🐛 Troubleshooting

### Common Issues

**Q: Voice recording not working**
- Ensure microphone permissions are granted
- Check if pyaudio is installed correctly
- Try typing answer instead

**Q: Questions not generating**
- Check if Gemini API key is set
- Verify internet connection
- Check logs for specific errors

**Q: PDF export failing**
- Ensure reportlab is installed
- Check write permissions for reports folder

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- OpenAI Whisper for speech recognition
- Microsoft Edge TTS for text-to-speech
- Streamlit for the web interface

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Email: support@example.com

---

**Built with ❤️ for interview preparation**
