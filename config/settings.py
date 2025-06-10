import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """
    Centralized configuration management for the LinkedIn automation tool.
    This class handles all settings, credentials, and preferences.
    """
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load all configuration settings from environment variables"""
        
        # LinkedIn Authentication
        self.LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
        self.LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
        
        # Validate required credentials
        if not self.LINKEDIN_EMAIL or not self.LINKEDIN_PASSWORD:
            raise ValueError("LinkedIn credentials must be set in .env file")
        
        # Browser Configuration
        self.CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', 'auto')
        self.HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
        
        # Application Limits and Timing
        self.MAX_APPLICATIONS_PER_DAY = int(os.getenv('MAX_APPLICATIONS_PER_DAY', 50))
        self.DELAY_BETWEEN_APPLICATIONS = int(os.getenv('DELAY_BETWEEN_APPLICATIONS', 30))
        
        # Job Search Preferences
        self.DEFAULT_LOCATION = os.getenv('DEFAULT_LOCATION', 'London, UK')
        self.DEFAULT_KEYWORDS = os.getenv('DEFAULT_KEYWORDS', '').split(',')
        
        # File Paths
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.RESUME_DIR = os.path.join(self.BASE_DIR, 'resumes')
        self.LOG_DIR = os.path.join(self.DATA_DIR, 'logs')
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [self.DATA_DIR, self.LOG_DIR, self.RESUME_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @property
    def job_search_config(self) -> Dict[str, Any]:
        """Return job search configuration as a dictionary"""
        return {
            'keywords': [kw.strip() for kw in self.DEFAULT_KEYWORDS if kw.strip()],
            'locations': [self.DEFAULT_LOCATION],
            'experience_levels': ['Entry level', 'Intership', 'Graduate', 'Off-Cycle', 'Junior'],
            'job_types': ['Full-time', 'Internship', 'Contract','Part-time', 'Graduate', 'Junior'],
            'date_posted': '1week',
            'easy_apply_only': True,
            'max_applications_per_day': self.MAX_APPLICATIONS_PER_DAY,
            'similarity_threshold': 0.6
        }
    
    @property
    def chrome_options(self) -> List[str]:
        """Return Chrome browser options for Selenium"""
        options = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        if self.HEADLESS_MODE:
            options.extend(['--headless', '--disable-gpu'])
        
        return options

# Global configuration instance
config = Config()
