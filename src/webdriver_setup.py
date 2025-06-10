from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import config
import logging

def setup_chrome_driver():
    """
    Set up Chrome WebDriver with optimal settings for LinkedIn automation.
    This function handles driver installation and configuration automatically.
    """
    logger = logging.getLogger('LinkedInAutomation')
    
    try:
        # Configure Chrome options
        chrome_options = Options()
        
        # Add all configuration options
        for option in config.chrome_options:
            chrome_options.add_argument(option)
        
        # Additional stealth options to avoid detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set up Chrome service
        if config.CHROME_DRIVER_PATH == 'auto':
            # Automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            logger.info("Using automatically managed ChromeDriver")
        else:
            # Use specified ChromeDriver path
            service = Service(config.CHROME_DRIVER_PATH)
            logger.info(f"Using ChromeDriver at: {config.CHROME_DRIVER_PATH}")
        
        # Create WebDriver instance
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to hide automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set window size for consistent behavior
        if not config.HEADLESS_MODE:
            driver.set_window_size(1920, 1080)
        
        logger.info("Chrome WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        raise
