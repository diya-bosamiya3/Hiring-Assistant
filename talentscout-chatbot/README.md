# TalentScout Hiring Assistant

An intelligent AI-powered chatbot designed to streamline the initial screening process for technology recruitment. Built with Streamlit and integrated with Large Language Models for natural conversation flow.

## 🎯 Project Overview

TalentScout Hiring Assistant is a conversational AI system that:
- Gathers essential candidate information through natural dialogue
- Generates technical questions based on declared tech stack
- Maintains context-aware conversations
- Ensures data privacy and security compliance
- Provides a seamless user experience for both candidates and recruiters

## 🚀 Features

### Core Functionality
- **Interactive Chat Interface**: Clean, intuitive Streamlit-based UI
- **Information Gathering**: Collects name, contact details, experience, and tech stack
- **Dynamic Question Generation**: Creates relevant technical questions based on candidate's expertise
- **Context Management**: Maintains conversation flow and handles follow-up questions
- **Graceful Exit**: Handles conversation endings with appropriate next steps

### Technical Capabilities
- **LLM Integration**: Supports multiple language models (GPT-3/4, etc.)
- **Data Privacy**: Implements encryption and data retention policies
- **Input Validation**: Ensures data integrity with comprehensive validation
- **Session Management**: Tracks conversation state and candidate progress

## 📋 Requirements

### System Requirements
- Python 3.8+
- Streamlit 1.28.0+
- OpenAI API access (or alternative LLM provider)

### Dependencies
\`\`\`
streamlit>=1.28.0
openai>=1.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
regex>=2023.0.0
\`\`\`

## 🛠️ Installation

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd talentscout-chatbot
   \`\`\`

2. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Set up environment variables**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   \`\`\`

4. **Run the application**
   \`\`\`bash
   streamlit run app.py
   \`\`\`

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for LLM integration
- `DEBUG_MODE`: Enable/disable debug logging
- `ENCRYPT_DATA`: Enable data encryption (recommended: True)
- `DATA_RETENTION_DAYS`: Number of days to retain candidate data

### Tech Stack Categories
The system recognizes technologies across multiple categories:
- Programming Languages (Python, JavaScript, Java, etc.)
- Frameworks (React, Django, Spring Boot, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Cloud Platforms (AWS, Google Cloud, Azure, etc.)
- Development Tools (Git, Docker, Kubernetes, etc.)

## 📖 Usage Guide

### For Candidates
1. Access the chatbot interface
2. Follow the conversational prompts to provide information
3. Declare your tech stack when asked
4. Answer generated technical questions
5. Complete the session and await next steps

### For Recruiters
1. Monitor candidate sessions through the admin interface
2. Review collected information and technical responses
3. Use the data for initial screening decisions
4. Follow up with qualified candidates

## 🏗️ Architecture

### Project Structure
\`\`\`
talentscout-chatbot/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── utils/
│   ├── data_handler.py   # Data storage and privacy
│   └── validators.py     # Input validation utilities
├── data/                 # Candidate data storage
└── README.md            # Project documentation
\`\`\`

### Key Components
- **HiringAssistant Class**: Core chatbot logic and conversation management
- **CandidateInfo DataClass**: Structured data storage for candidate information
- **DataHandler**: Secure data storage with privacy compliance
- **InputValidator**: Comprehensive input validation and sanitization

## 🔒 Data Privacy & Security

### Privacy Measures
- **Email Hashing**: Personal emails are hashed for anonymization
- **Data Encryption**: Sensitive information is encrypted at rest
- **Retention Policy**: Automatic cleanup of old data based on retention settings
- **GDPR Compliance**: Designed with data protection regulations in mind

### Security Features
- Input validation and sanitization
- Secure session management
- Error handling without data exposure
- Configurable data retention policies

## 🧠 Prompt Engineering

### Design Principles
- **Context Awareness**: Prompts maintain conversation context
- **Tech Stack Adaptation**: Questions dynamically generated based on declared technologies
- **Natural Flow**: Conversational prompts feel natural and engaging
- **Error Handling**: Graceful handling of unexpected inputs

### Question Generation Strategy
- Analyze declared tech stack
- Map technologies to relevant question categories
- Generate 3-5 targeted questions per technology
- Ensure appropriate difficulty levels
- Maintain conversation coherence

## 🚧 Development Status

This project is currently in development with the following milestones:

- [x] Project Structure Setup
- [ ] Streamlit Interface Implementation
- [ ] LLM Integration and Prompt Engineering
- [ ] Information Gathering System
- [ ] Technical Question Generation
- [ ] Conversation Management
- [ ] Data Privacy Features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or support, please contact the development team or open an issue in the repository.
