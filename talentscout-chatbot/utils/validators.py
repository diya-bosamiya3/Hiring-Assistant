import re
from typing import List, Tuple

class InputValidator:
    """Validate user inputs for data integrity"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, "Valid email"
        return False, "Please enter a valid email address"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number format"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-$$$$\.]+', '', phone)
        
        # Check if it's a valid phone number (10-15 digits)
        if re.match(r'^\+?[1-9]\d{9,14}$', cleaned):
            return True, "Valid phone number"
        return False, "Please enter a valid phone number (10-15 digits)"
    
    @staticmethod
    def validate_experience(experience: str) -> Tuple[bool, str]:
        """Validate years of experience"""
        try:
            years = float(experience)
            if 0 <= years <= 50:
                return True, "Valid experience"
            return False, "Please enter experience between 0 and 50 years"
        except ValueError:
            return False, "Please enter a valid number for years of experience"
    
    @staticmethod
    def extract_tech_stack(text: str, available_techs: List[str]) -> List[str]:
        """Extract mentioned technologies from text"""
        found_techs = []
        text_lower = text.lower()
        
        for tech in available_techs:
            if tech.lower() in text_lower:
                found_techs.append(tech)
        
        return found_techs
