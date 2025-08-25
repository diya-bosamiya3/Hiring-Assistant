import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'TalentScout Hiring Assistant')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Data Privacy
    ENCRYPT_DATA = os.getenv('ENCRYPT_DATA', 'True').lower() == 'true'
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '30'))
    
    # Tech Stack Categories
    TECH_CATEGORIES = {
        'programming_languages': [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 
            'TypeScript', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala'
        ],
        'frameworks': [
            'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'FastAPI',
            'Spring Boot', 'Express.js', 'Next.js', 'Laravel', 'Rails'
        ],
        'databases': [
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite',
            'Oracle', 'Cassandra', 'DynamoDB', 'Elasticsearch'
        ],
        'cloud_platforms': [
            'AWS', 'Google Cloud', 'Azure', 'Heroku', 'Vercel',
            'Netlify', 'DigitalOcean', 'Kubernetes', 'Docker'
        ],
        'tools': [
            'Git', 'Jenkins', 'Docker', 'Kubernetes', 'Terraform',
            'Ansible', 'Prometheus', 'Grafana', 'Jira', 'Confluence'
        ]
    }
