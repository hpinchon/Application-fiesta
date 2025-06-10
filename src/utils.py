import logging
import os
import time
import random
from datetime import datetime
from typing import Optional

# Import the Config class and create an instance
from config.settings import Config
config = Config()

def setup_logging() -> logging.Logger:
    """
    Set up comprehensive logging for the application.
    This is essential for debugging and monitoring automation.
    """
    
    # Create log filename with timestamp
    log_filename = f"linkedin_automation_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(config.LOG_DIR, log_filename)
    
    # Configure logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    logger = logging.getLogger('LinkedInAutomation')
    logger.info("=== LinkedIn Automation Session Started ===")
    
    return logger


def human_delay(min_seconds: int = 2, max_seconds: int = 5) -> None:
    """
    Add random delays to mimic human behavior and avoid detection.
    This is crucial for avoiding LinkedIn's anti-bot measures.
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def safe_find_element(driver, by, value, timeout: int = 10, required: bool = True):
    """
    Safely find elements with proper error handling and logging.
    This prevents crashes when elements aren't found.
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        if required:
            logger = logging.getLogger('LinkedInAutomation')
            logger.error(f"Required element not found: {by}={value}")
            raise
        return None
    except NoSuchElementException:
        if required:
            logger = logging.getLogger('LinkedInAutomation')
            logger.error(f"Element does not exist: {by}={value}")
            raise
        return None

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def clean_text(text: str) -> str:
    """Clean and normalize text for processing"""
    if not text:
        return ""
    
    import re
    # Remove extra whitespace and special characters
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s.-]', '', text)
    return text

def get_current_date_string() -> str:
    """Get current date as formatted string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_applications_today(csv_path: str) -> int:
    """Count applications submitted today"""
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        today = datetime.now().strftime('%Y-%m-%d')
        today_applications = df[df['application_date'].str.contains(today, na=False)]
        return len(today_applications)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return 0
    except Exception as e:
        logger = logging.getLogger('LinkedInAutomation')
        logger.error(f"Error counting today's applications: {e}")
        return 0
