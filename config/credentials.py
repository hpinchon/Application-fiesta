import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', 'your_email@example.com')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', 'your_password')

# Chrome driver path
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', './Applications/Google Chrome.app')
