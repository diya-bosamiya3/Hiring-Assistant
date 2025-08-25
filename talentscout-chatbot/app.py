import streamlit as st
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import openai
from dataclasses import dataclass, asdict
import os
import uuid

# Configure page
st.set_page_config(
    page_title="TalentScout - Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@dataclass
class CandidateInfo:
    """Data class to store candidate information"""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    years_experience: str = ""
    desired_positions: str = ""
    current_location: str = ""
    tech_stack: List[str] = None
    
    def __post_init__(self):
        if self.tech_stack is None:
            self.tech_stack = []

from llm.llm_client import LLMClient
from llm.prompt_manager import PromptManager
from utils.validators import InputValidator
from utils.data_handler import DataHandler

class HiringAssistant:
    """Main chatbot class for handling conversations and LLM interactions"""
    
    def __init__(self):
        self.conversation_ended = False
        self.current_stage = "greeting"
        self.candidate_info = CandidateInfo()
        self.technical_questions = []
        self.conversation_history = []
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
        self.validator = InputValidator()
        self.current_question_index = 0
        self.data_handler = DataHandler()
        
    def initialize_llm(self):
        """Initialize the LLM client"""
        self.llm_client.initialize_client()
    
    def generate_response(self, user_input: str) -> str:
        """Generate chatbot response based on user input"""
        
        # Add user input to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Determine current stage and generate appropriate response
        response = self._process_user_input(user_input)
        
        # Add assistant response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _process_user_input(self, user_input: str) -> str:
        """Process user input based on current conversation stage"""
        
        if self.current_stage == "greeting":
            return self._handle_greeting_stage(user_input)
        elif self.current_stage == "personal_info":
            return self._handle_personal_info_stage(user_input)
        elif self.current_stage == "tech_stack":
            return self._handle_tech_stack_stage(user_input)
        elif self.current_stage == "technical_questions":
            return self._handle_technical_questions_stage(user_input)
        else:
            return self._generate_contextual_response(user_input)
    
    def _handle_greeting_stage(self, user_input: str) -> str:
        """Handle the initial greeting and name collection"""
        
        # Extract name from input
        name = user_input.strip()
        if len(name) > 2 and not any(char.isdigit() for char in name):
            self.candidate_info.full_name = name
            self.current_stage = "personal_info"
            return f"Nice to meet you, {name}! Now, could you please provide your email address?"
        else:
            return "I'd like to get your full name to personalize our conversation. Could you please tell me your name?"
    
    def _handle_personal_info_stage(self, user_input: str) -> str:
        """Handle personal information gathering"""
        
        # Determine what information we're missing
        missing_fields = []
        if not self.candidate_info.email:
            missing_fields.append('email')
        if not self.candidate_info.phone:
            missing_fields.append('phone')
        if not self.candidate_info.years_experience:
            missing_fields.append('years_experience')
        if not self.candidate_info.desired_positions:
            missing_fields.append('desired_positions')
        if not self.candidate_info.current_location:
            missing_fields.append('current_location')
        
        if not missing_fields:
            self.current_stage = "tech_stack"
            return "Perfect! Now, could you tell me about your technical expertise? Please list the main programming languages, frameworks, databases, and tools you work with."
        
        # Process current input based on what we're expecting
        current_field = missing_fields[0]
        
        if current_field == 'email':
            is_valid, message = self.validator.validate_email(user_input)
            if is_valid:
                self.candidate_info.email = user_input.strip()
                return "Great! What's your phone number?"
            else:
                return f"That doesn't look like a valid email address. {message}"
        
        elif current_field == 'phone':
            is_valid, message = self.validator.validate_phone(user_input)
            if is_valid:
                self.candidate_info.phone = user_input.strip()
                return "Perfect! How many years of professional experience do you have in technology?"
            else:
                return f"That doesn't look like a valid phone number. {message}"
        
        elif current_field == 'years_experience':
            is_valid, message = self.validator.validate_experience(user_input)
            if is_valid:
                self.candidate_info.years_experience = user_input.strip()
                return "Excellent! What type of positions are you looking for? (e.g., Software Engineer, Data Scientist, DevOps Engineer)"
            else:
                return f"Please provide a valid number of years. {message}"
        
        elif current_field == 'desired_positions':
            self.candidate_info.desired_positions = user_input.strip()
            return "Great! What's your current location or preferred work location?"
        
        elif current_field == 'current_location':
            self.candidate_info.current_location = user_input.strip()
            self.current_stage = "tech_stack"
            return "Perfect! Now, could you tell me about your technical expertise? Please list the main programming languages, frameworks, databases, and tools you work with."
        
        return "Thank you for that information. Let me continue gathering your details."
    
    def _handle_tech_stack_stage(self, user_input: str) -> str:
        """Handle tech stack identification and analysis"""
        
        # Extract technologies from user input
        extracted_techs = self.llm_client.extract_tech_stack(user_input)
        
        if extracted_techs:
            self.candidate_info.tech_stack = extracted_techs
            self.current_stage = "technical_questions"
            
            # Generate technical questions
            self._generate_technical_questions()
            
            tech_list = ", ".join(extracted_techs)
            return f"Excellent! I can see you work with {tech_list}. That's a great tech stack! Now I'd like to ask you a few technical questions to better understand your expertise. Let's start with the first question:\n\n{self.technical_questions[0] if self.technical_questions else 'Can you tell me about a challenging project you worked on recently?'}"
        else:
            return "I'd like to learn more about your technical skills. Could you please list the specific programming languages, frameworks, databases, and tools you use regularly? For example: Python, React, PostgreSQL, Docker, etc."
    
    def _handle_technical_questions_stage(self, user_input: str) -> str:
        """Handle technical question responses"""
        
        # Record the answer
        if self.current_question_index < len(self.technical_questions):
            # Move to next question
            self.current_question_index += 1
            
            if self.current_question_index < len(self.technical_questions):
                return f"Thank you for that detailed answer! Here's the next question:\n\n{self.technical_questions[self.current_question_index]}"
            else:
                # All questions completed
                self.current_stage = "complete"
                return """🎉 **Excellent work!** You've completed all the technical questions.

Thank you for taking the time to go through this screening process. Your responses show great technical knowledge and experience.

**What happens next:**
- Our technical team will review your responses within 24-48 hours
- If there's a good match, we'll reach out to schedule a more detailed interview
- You should hear back from us within 3-5 business days

**Keep an eye on:**
- Your email for updates and next steps
- Your phone for potential follow-up calls

Thank you for your interest in opportunities with TalentScout. We're excited about the possibility of working with you!

Feel free to type 'bye' if you'd like to end our conversation, or ask any questions you might have."""
        
        return "Thank you for your response. Let me continue with the next question."
    
    def _generate_technical_questions(self):
        """Generate technical questions based on candidate's tech stack"""
        
        if not self.candidate_info.tech_stack:
            self.technical_questions = [
                "Can you describe a challenging technical problem you solved recently?",
                "How do you handle debugging when something isn't working as expected?",
                "What's your process for learning new technologies?"
            ]
            return
        
        # Generate questions based on experience level and tech stack
        experience_years = self.candidate_info.years_experience
        tech_stack = self.candidate_info.tech_stack
        
        questions = []
        
        # Programming language questions
        if any(lang in tech_stack for lang in ['Python', 'JavaScript', 'Java', 'C++', 'C#']):
            questions.append("Can you explain the difference between synchronous and asynchronous programming, and when you would use each approach?")
        
        # Framework questions
        if any(framework in tech_stack for framework in ['React', 'Angular', 'Vue.js', 'Django', 'Flask']):
            questions.append("How do you handle state management in your applications, and what patterns do you prefer?")
        
        # Database questions
        if any(db in tech_stack for db in ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis']):
            questions.append("How would you optimize a slow database query, and what tools would you use to identify the bottleneck?")
        
        # Cloud/DevOps questions
        if any(cloud in tech_stack for cloud in ['AWS', 'Google Cloud', 'Azure', 'Docker', 'Kubernetes']):
            questions.append("Can you walk me through how you would deploy a web application to production, including considerations for scalability and monitoring?")
        
        # General problem-solving question
        questions.append("Describe a time when you had to work with a technology you weren't familiar with. How did you approach learning it?")
        
        # Limit to 3-5 questions
        self.technical_questions = questions[:5]
    
    def _generate_contextual_response(self, user_input: str) -> str:
        """Generate contextual response using LLM"""
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": self.prompt_manager.get_system_prompt()},
            {"role": "system", "content": self.prompt_manager.get_conversation_context_prompt(
                self.conversation_history, self.current_stage
            )}
        ]
        
        # Add recent conversation history
        recent_history = self.conversation_history[-4:] if len(self.conversation_history) > 4 else self.conversation_history
        messages.extend(recent_history)
        
        return self.llm_client.generate_response(messages)
    
    def is_conversation_ending(self, user_input: str) -> bool:
        """Check if user wants to end conversation"""
        ending_keywords = ["bye", "goodbye", "exit", "quit", "end", "stop", "thanks", "thank you"]
        return any(keyword in user_input.lower() for keyword in ending_keywords)
    
    def save_session_data(self, session_id: str) -> bool:
        """Save current session data securely"""
        return self.data_handler.save_candidate_data(
            self.candidate_info, 
            session_id, 
            self.conversation_history
        )
    
    def export_session_data(self, session_id: str) -> Optional[str]:
        """Export session data for GDPR compliance"""
        return self.data_handler.export_candidate_data(session_id)
    
    def delete_session_data(self, session_id: str) -> bool:
        """Delete session data (right to erasure)"""
        return self.data_handler.delete_candidate_data(session_id, 'user_request')

def main():
    """Main Streamlit application"""
    
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main Container */
    .main-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        max-width: 800px;
        margin: 2rem auto;
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        color: #2c3e50;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Chat Container */
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Message Styles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 20%;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    .bot-message {
        background: white;
        color: #2c3e50;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 20% 8px 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        animation: slideInLeft 0.3s ease-out;
    }
    
    /* Progress Indicator */
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .progress-step {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin: 0 4px;
        transition: all 0.3s ease;
    }
    
    .progress-step.completed {
        background: #28a745;
    }
    
    .progress-step.current {
        background: #667eea;
        transform: scale(1.2);
    }
    
    .progress-step.pending {
        background: #dee2e6;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    .status-gathering {
        background: #e3f2fd;
        color: #1976d2;
    }
    
    .status-questions {
        background: #f3e5f5;
        color: #7b1fa2;
    }
    
    .status-complete {
        background: #e8f5e8;
        color: #2e7d32;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 12px 20px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Animations */
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Sidebar Styling */
    .sidebar-content {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎯 TalentScout</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI-powered recruitment companion for seamless candidate screening</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'assistant' not in st.session_state:
        st.session_state.assistant = HiringAssistant()
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting
        greeting = """
        👋 Hello! Welcome to TalentScout's Hiring Assistant. 
        
        I'm here to help streamline your interview process. I'll gather some essential information about your background and ask relevant technical questions based on your expertise.
        
        This should take about 5-10 minutes. Ready to get started?
        
        **Let's begin with your full name:**
        """
        st.session_state.messages.append({"role": "assistant", "content": greeting})
    
    progress_steps = [
        "Personal Info", "Experience", "Tech Stack", "Technical Questions", "Complete"
    ]
    
    current_step = 0
    if hasattr(st.session_state.assistant, 'current_stage'):
        stage_mapping = {
            "greeting": 0,
            "personal_info": 0,
            "experience": 1,
            "tech_stack": 2,
            "technical_questions": 3,
            "complete": 4
        }
        current_step = stage_mapping.get(st.session_state.assistant.current_stage, 0)
    
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown("**Interview Progress:**")
    
    progress_html = ""
    for i, step in enumerate(progress_steps):
        if i < current_step:
            progress_html += f'<span class="progress-step completed" title="{step}"></span>'
        elif i == current_step:
            progress_html += f'<span class="progress-step current" title="{step}"></span>'
        else:
            progress_html += f'<span class="progress-step pending" title="{step}"></span>'
    
    progress_html += f'<span style="margin-left: 1rem; color: #666; font-size: 0.9rem;">{progress_steps[current_step]}</span>'
    st.markdown(progress_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    status_mapping = {
        "greeting": ("Gathering Information", "status-gathering"),
        "personal_info": ("Gathering Information", "status-gathering"),
        "experience": ("Gathering Information", "status-gathering"),
        "tech_stack": ("Analyzing Tech Stack", "status-gathering"),
        "technical_questions": ("Technical Assessment", "status-questions"),
        "complete": ("Interview Complete", "status-complete")
    }
    
    status_text, status_class = status_mapping.get(st.session_state.assistant.current_stage, ("Getting Started", "status-gathering"))
    st.markdown(f'<span class="status-badge {status_class}">📋 {status_text}</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    if not st.session_state.assistant.conversation_ended:
        placeholder_text = "Type your response here..."
        if st.session_state.assistant.current_stage == "greeting":
            placeholder_text = "Enter your full name..."
        elif st.session_state.assistant.current_stage == "personal_info":
            placeholder_text = "Provide the requested information..."
        
        user_input = st.chat_input(placeholder_text)
        
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Check if conversation should end
            if st.session_state.assistant.is_conversation_ending(user_input):
                st.session_state.assistant.conversation_ended = True
                st.session_state.assistant.current_stage = "complete"
                farewell = """
                🎉 **Thank you for completing the screening process!**
                
                Your information has been successfully recorded and our recruitment team will review your profile carefully.
                
                **Next steps:**
                - ✅ Our team will evaluate your responses within 24-48 hours
                - 📧 If you're a good fit, we'll contact you within 3-5 business days
                - 📱 Keep an eye on your email and phone for updates
                
                **What happens next?**
                - Technical review of your responses
                - Potential follow-up interview scheduling
                - Reference checks for qualified candidates
                
                Thank you for your interest in opportunities with TalentScout. We appreciate the time you've invested in this process!
                
                Have a great day and good luck with your job search! 🚀
                """
                st.session_state.messages.append({"role": "assistant", "content": farewell})
            else:
                # Generate response (placeholder for now)
                response = st.session_state.assistant.generate_response(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()
    else:
        st.success("🎉 Interview completed successfully!")
        st.info("💡 **Tip:** Refresh the page to start a new screening session.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Start New Session", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("📊 Session Dashboard")
        
        # Session info
        st.subheader("Current Session")
        st.write(f"**Stage:** {st.session_state.assistant.current_stage.replace('_', ' ').title()}")
        st.write(f"**Status:** {'Completed' if st.session_state.assistant.conversation_ended else 'In Progress'}")
        st.write(f"**Messages:** {len(st.session_state.messages)}")
        
        # Candidate info preview (if available)
        if hasattr(st.session_state.assistant, 'candidate_info'):
            candidate = st.session_state.assistant.candidate_info
            st.subheader("📝 Collected Information")
            
            if candidate.full_name:
                st.write(f"**Name:** {candidate.full_name}")
            if candidate.email:
                st.write(f"**Email:** {candidate.email}")
            if candidate.years_experience:
                st.write(f"**Experience:** {candidate.years_experience} years")
            if candidate.tech_stack:
                st.write(f"**Tech Stack:** {', '.join(candidate.tech_stack[:3])}{'...' if len(candidate.tech_stack) > 3 else ''}")
        
        st.divider()
        
        # Admin controls
        st.subheader("🔧 Session Controls")
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        if st.button("💾 Export Data", use_container_width=True):
            if hasattr(st.session_state, 'session_id'):
                # Save current session first
                st.session_state.assistant.save_session_data(st.session_state.session_id)
                
                # Export data
                export_file = st.session_state.assistant.export_session_data(st.session_state.session_id)
                if export_file:
                    st.success("✅ Data exported successfully!")
                    st.info(f"📁 Export saved to: {export_file}")
                    
                    # Provide download option
                    try:
                        with open(export_file, 'r') as f:
                            export_data = f.read()
                        
                        st.download_button(
                            label="📥 Download Export",
                            data=export_data,
                            file_name=f"talentscout_export_{st.session_state.session_id[:8]}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error preparing download: {e}")
                else:
                    st.error("❌ Export failed. Please try again.")
            else:
                st.warning("⚠️ No session data to export.")
        
        if st.button("🗑️ Delete My Data", use_container_width=True):
            if hasattr(st.session_state, 'session_id'):
                if st.session_state.assistant.delete_session_data(st.session_state.session_id):
                    st.success("✅ Your data has been permanently deleted.")
                    st.info("🔄 Starting new session...")
                    # Clear session and restart
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
                else:
                    st.error("❌ Data deletion failed. Please contact support.")
            else:
                st.warning("⚠️ No session data to delete.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("🔒 Privacy & Data Protection"):
            st.markdown("""
            **Your Privacy Matters:**
            
            🔐 **Data Encryption:** All personal information is encrypted at rest
            
            🕒 **Retention Policy:** Data is automatically deleted after 30 days
            
            📋 **Your Rights (GDPR):**
            - **Access:** View your stored data
            - **Portability:** Export your data
            - **Erasure:** Delete your data anytime
            - **Rectification:** Correct inaccurate data
            
            **What We Collect:**
            - Contact information (encrypted)
            - Professional experience
            - Technical skills
            - Interview responses
            
            **Data Usage:**
            - Initial candidate screening only
            - No sharing with third parties
            - Secure processing and storage
            
            **Contact:** privacy@talentscout.com
            """)
        
        with st.expander("❓ Help & Tips"):
            st.markdown("""
            **How to use TalentScout:**
            
            1. **Be honest** - Provide accurate information
            2. **Be specific** - Detail your tech stack clearly  
            3. **Take your time** - No rush, think through answers
            4. **Ask questions** - Feel free to clarify anything
            
            **Technical Issues?**
            - Refresh the page if something seems stuck
            - Use the Reset Session button to start over
            - Contact support if problems persist
            """)

if __name__ == "__main__":
    main()
