import openai
from typing import List, Dict, Optional
from config import Config
import json
import re

class LLMClient:
    """Client for interacting with OpenAI's API"""
    
    def __init__(self):
        self.config = Config()
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize the OpenAI client"""
        try:
            if self.config.OPENAI_API_KEY:
                openai.api_key = self.config.OPENAI_API_KEY
                self.client = openai
            else:
                print("Warning: OpenAI API key not found. Using mock responses.")
                self.client = None
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            self.client = None
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 300, temperature: float = 0.7) -> str:
        """Generate response using OpenAI API"""
        
        if not self.client:
            return self._get_mock_response(messages)
        
        try:
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._get_fallback_response()
    
    def extract_tech_stack(self, user_input: str) -> List[str]:
        """Extract mentioned technologies from user input"""
        
        found_techs = []
        user_input_lower = user_input.lower()
        
        # Get all available technologies
        all_techs = []
        for category, techs in self.config.TECH_CATEGORIES.items():
            all_techs.extend(techs)
        
        # Find mentioned technologies
        for tech in all_techs:
            # Check for exact matches and common variations
            tech_variations = [
                tech.lower(),
                tech.lower().replace('.', ''),
                tech.lower().replace(' ', ''),
                tech.lower().replace('-', ''),
            ]
            
            for variation in tech_variations:
                if variation in user_input_lower:
                    if tech not in found_techs:
                        found_techs.append(tech)
                    break
        
        return found_techs
    
    def _get_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate mock responses when API is not available"""
        
        last_message = messages[-1]['content'].lower() if messages else ""
        
        # Mock responses based on conversation context
        if "name" in last_message and len(messages) <= 3:
            return "Thank you! Now, could you please provide your email address?"
        
        elif "@" in last_message:
            return "Great! What's your phone number?"
        
        elif any(char.isdigit() for char in last_message) and ("phone" in messages[-2]['content'].lower() if len(messages) > 1 else False):
            return "Perfect! How many years of professional experience do you have in technology?"
        
        elif "year" in last_message or any(word in last_message for word in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
            return "Excellent! What type of positions are you looking for? (e.g., Software Engineer, Data Scientist, DevOps Engineer)"
        
        elif any(word in last_message for word in ["engineer", "developer", "scientist", "analyst", "manager"]):
            return "Great! What's your current location or preferred work location?"
        
        elif any(word in last_message for word in ["city", "remote", "location", "state", "country"]):
            return "Perfect! Now, could you tell me about your technical expertise? Please list the main programming languages, frameworks, databases, and tools you work with."
        
        elif any(tech.lower() in last_message for tech in ["python", "javascript", "java", "react", "node", "sql", "aws", "docker"]):
            return "Excellent tech stack! Now I'd like to ask you a few technical questions to better understand your expertise. Let's start with: Can you explain the difference between synchronous and asynchronous programming, and when you would use each approach?"
        
        else:
            return "Thank you for that information. Could you tell me more about your background?"
    
    def _get_fallback_response(self) -> str:
        """Fallback response when API fails"""
        return "I apologize, but I'm experiencing some technical difficulties. Could you please repeat your last response?"
