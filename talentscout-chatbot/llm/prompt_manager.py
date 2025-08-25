from typing import List, Dict, Any
from config import Config

class PromptManager:
    """Manages prompts for different conversation stages"""
    
    def __init__(self):
        self.config = Config()
    
    def get_system_prompt(self) -> str:
        """Get the main system prompt for the hiring assistant"""
        return """You are TalentScout's AI Hiring Assistant, a professional and friendly recruitment chatbot specializing in technology placements. Your role is to conduct initial candidate screening through natural conversation.

CORE RESPONSIBILITIES:
1. Gather essential candidate information (name, email, phone, experience, location, desired positions)
2. Identify candidate's tech stack and expertise areas
3. Generate relevant technical questions based on their declared technologies
4. Maintain professional, encouraging, and conversational tone
5. Keep responses concise but informative (2-3 sentences max unless asking technical questions)

CONVERSATION FLOW:
- Start with greeting and brief explanation
- Collect personal information one piece at a time
- Ask about experience and desired positions
- Identify tech stack through natural conversation
- Generate 3-5 technical questions based on their expertise
- Conclude professionally with next steps

IMPORTANT GUIDELINES:
- Always be encouraging and positive
- Ask for one piece of information at a time
- Validate information when possible
- If user provides multiple pieces of info at once, acknowledge all but focus on what's missing
- For tech stack, ask them to list their main technologies, frameworks, and tools
- Generate technical questions that are practical and relevant to their experience level
- Never ask inappropriate personal questions
- If user wants to end conversation, be gracious and provide next steps

TONE: Professional yet friendly, encouraging, efficient but not rushed."""

    def get_information_gathering_prompt(self, missing_fields: List[str], candidate_info: Dict) -> str:
        """Generate prompt for gathering missing candidate information"""
        
        field_questions = {
            'full_name': "Could you please tell me your full name?",
            'email': "What's your email address?",
            'phone': "Could you provide your phone number?",
            'years_experience': "How many years of professional experience do you have in technology?",
            'desired_positions': "What type of positions are you looking for? (e.g., Software Engineer, Data Scientist, etc.)",
            'current_location': "What's your current location or preferred work location?",
            'tech_stack': "Could you tell me about your technical expertise? Please list the main programming languages, frameworks, databases, and tools you work with."
        }
        
        if not missing_fields:
            return "Great! I have all your basic information. Now let's move on to some technical questions."
        
        next_field = missing_fields[0]
        question = field_questions.get(next_field, "Could you provide more information?")
        
        # Add context about what we already have
        collected_info = []
        for field, value in candidate_info.items():
            if value and field != 'tech_stack':
                collected_info.append(f"{field.replace('_', ' ').title()}: {value}")
        
        context = ""
        if collected_info:
            context = f"Thanks for the information so far. "
        
        return f"{context}{question}"

    def get_tech_stack_analysis_prompt(self, tech_input: str) -> str:
        """Generate prompt to analyze and extract tech stack from user input"""
        
        all_techs = []
        for category, techs in self.config.TECH_CATEGORIES.items():
            all_techs.extend(techs)
        
        return f"""Analyze the following text and extract mentioned technologies, frameworks, databases, and tools. 
        
User input: "{tech_input}"

Available technologies to match against: {', '.join(all_techs)}

Please:
1. Identify all mentioned technologies from the available list
2. Categorize them (programming languages, frameworks, databases, cloud platforms, tools)
3. Respond in a conversational way acknowledging their tech stack
4. If they mention experience levels or years with specific technologies, note that
5. Ask if there are any other important technologies they work with that weren't mentioned

Format your response as a natural conversation, not a list."""

    def get_technical_questions_prompt(self, tech_stack: List[str], experience_level: str) -> str:
        """Generate technical questions based on candidate's tech stack"""
        
        return f"""Generate 3-5 relevant technical questions for a candidate with {experience_level} years of experience who works with: {', '.join(tech_stack)}

QUESTION GUIDELINES:
- Mix of conceptual and practical questions
- Appropriate for their experience level
- Cover different technologies they mentioned
- Include at least one problem-solving scenario
- Questions should assess both knowledge and practical application
- Avoid overly complex or trick questions
- Make questions conversational, not like an exam

EXPERIENCE LEVEL CONSIDERATIONS:
- 0-2 years: Focus on fundamentals, basic concepts, simple scenarios
- 3-5 years: Intermediate concepts, design patterns, best practices
- 6+ years: Advanced topics, architecture decisions, leadership scenarios

Present the questions in a friendly, conversational manner. Introduce them by saying something like "Now I'd like to ask you a few technical questions to better understand your expertise."

Ask questions one at a time, waiting for responses before moving to the next question."""

    def get_conversation_context_prompt(self, conversation_history: List[Dict], current_stage: str) -> str:
        """Generate context-aware prompt based on conversation history"""
        
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        
        context = "RECENT CONVERSATION:\n"
        for msg in recent_messages:
            role = "Candidate" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        stage_instructions = {
            'greeting': 'You are in the greeting stage. Welcome the candidate and start gathering basic information.',
            'personal_info': 'You are gathering personal information. Ask for missing details one at a time.',
            'experience': 'You are learning about their experience and desired positions.',
            'tech_stack': 'You are identifying their technical expertise and skills.',
            'technical_questions': 'You are asking technical questions based on their declared expertise.',
            'complete': 'The screening is complete. Provide next steps and conclude professionally.'
        }
        
        instruction = stage_instructions.get(current_stage, 'Continue the conversation naturally.')
        
        return f"{context}\nCURRENT STAGE: {current_stage}\nINSTRUCTION: {instruction}\n\nRespond naturally and conversationally based on the context above."
