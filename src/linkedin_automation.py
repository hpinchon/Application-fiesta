import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from config.settings import Config
from src.utils import human_delay, safe_find_element
from src.webdriver_setup import setup_chrome_driver

class LinkedInApplicationBot:
    """
    Advanced LinkedIn application automation system that submits job applications
    while maintaining human-like behavior patterns to avoid detection.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('LinkedInAutomation')
        self.driver = None
        self.is_logged_in = False
        self.application_count = 0
        self.session_stats = {
            'applications_attempted': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'login_attempts': 0,
            'session_start_time': None
        }
    
    def initialize_browser(self) -> bool:
        """Initialize Chrome browser with stealth settings."""
        try:
            self.driver = setup_chrome_driver()
            self.session_stats['session_start_time'] = time.time()
            self.logger.info("🌐 Browser initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize browser: {e}")
            return False
    
    def login_to_linkedin(self) -> bool:
        """
        Automated LinkedIn login with human-like behavior patterns.
        """
        try:
            self.logger.info("🔐 Attempting LinkedIn login...")
            self.session_stats['login_attempts'] += 1
            
            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            human_delay(2, 4)
            
            # Find and fill email field
            email_field = safe_find_element(
                self.driver, By.ID, "username", timeout=10
            )
            if not email_field:
                self.logger.error("❌ Email field not found")
                return False
            
            # Type email with human-like delays
            self._type_with_human_delay(email_field, self.config.LINKEDIN_EMAIL)
            human_delay(1, 2)
            
            # Find and fill password field
            password_field = safe_find_element(
                self.driver, By.ID, "password", timeout=10
            )
            if not password_field:
                self.logger.error("❌ Password field not found")
                return False
            
            # Type password with human-like delays
            self._type_with_human_delay(password_field, self.config.LINKEDIN_PASSWORD)
            human_delay(1, 2)
            
            # Click login button
            login_button = safe_find_element(
                self.driver, By.XPATH, "//button[@type='submit']", timeout=10
            )
            if not login_button:
                self.logger.error("❌ Login button not found")
                return False
            
            login_button.click()
            human_delay(3, 6)
            
            # Check if login was successful
            if self._verify_login_success():
                self.is_logged_in = True
                self.logger.info("✅ Successfully logged into LinkedIn")
                return True
            else:
                self.logger.error("❌ Login verification failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
            return False
    
    def _verify_login_success(self) -> bool:
        """Verify that login was successful by checking for LinkedIn feed."""
        try:
            # Look for elements that indicate successful login
            success_indicators = [
                (By.CLASS_NAME, "global-nav"),
                (By.XPATH, "//a[contains(@href, '/feed/')]"),
                (By.XPATH, "//button[contains(@class, 'global-nav')]")
            ]
            
            for by, value in success_indicators:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, value))
                    )
                    if element:
                        return True
                except TimeoutException:
                    continue
            
            # Check if we're still on login page or got redirected to challenge
            current_url = self.driver.current_url.lower()
            if 'login' in current_url or 'challenge' in current_url:
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Login verification error: {e}")
            return False
    
    def apply_to_job(self, job_data: Dict, cover_letter: str) -> bool:
        """
        Apply to a specific job with tailored application materials.
        """
        try:
            job_url = job_data.get('job_url', '')
            company = job_data.get('company', 'Unknown')
            title = job_data.get('title', 'Unknown')
            
            self.logger.info(f"🎯 Applying to: {company} - {title}")
            self.session_stats['applications_attempted'] += 1
            
            # Navigate to job posting
            self.driver.get(job_url)
            human_delay(3, 5)
            
            # Find and click Easy Apply button
            easy_apply_button = self._find_easy_apply_button()
            if not easy_apply_button:
                self.logger.warning(f"⚠️ Easy Apply not available for {company} - {title}")
                return False
            
            easy_apply_button.click()
            human_delay(2, 4)
            
            # Process application form(s)
            application_success = self._process_application_forms(job_data, cover_letter)
            
            if application_success:
                self.session_stats['applications_successful'] += 1
                self.application_count += 1
                self.logger.info(f"✅ Successfully applied to {company} - {title}")
                return True
            else:
                self.session_stats['applications_failed'] += 1
                self.logger.warning(f"❌ Failed to complete application for {company} - {title}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Application error for {company} - {title}: {e}")
            self.session_stats['applications_failed'] += 1
            return False
    
    def _find_easy_apply_button(self) -> Optional[object]:
        """Find the Easy Apply button using multiple selectors."""
        easy_apply_selectors = [
            "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]",
            "//button[contains(text(), 'Easy Apply')]",
            "//button[@data-control-name='jobdetails_topcard_inapply']",
            ".jobs-apply-button--top-card",
            ".jobs-s-apply button"
        ]
        
        for selector in easy_apply_selectors:
            try:
                if selector.startswith("//"):
                    element = safe_find_element(
                        self.driver, By.XPATH, selector, timeout=5, required=False
                    )
                else:
                    element = safe_find_element(
                        self.driver, By.CSS_SELECTOR, selector, timeout=5, required=False
                    )
                
                if element and element.is_enabled():
                    return element
            except Exception:
                continue
        
        return None
    
    def _process_application_forms(self, job_data: Dict, cover_letter: str) -> bool:
        """
        Process multi-step application forms with intelligent form filling.
        """
        max_steps = 5  # Prevent infinite loops
        current_step = 0
        
        while current_step < max_steps:
            human_delay(2, 4)
            current_step += 1
            
            # Check if we're done (submit button or confirmation)
            if self._is_application_complete():
                return True
            
            # Fill current form step
            form_filled = self._fill_current_form_step(job_data, cover_letter)
            
            if not form_filled:
                self.logger.warning(f"⚠️ Could not fill form step {current_step}")
                return False
            
            # Try to proceed to next step
            if not self._proceed_to_next_step():
                self.logger.warning(f"⚠️ Could not proceed from step {current_step}")
                return False
        
        self.logger.warning("⚠️ Maximum application steps reached")
        return False
    
    def _fill_current_form_step(self, job_data: Dict, cover_letter: str) -> bool:
        """Fill the current step of the application form."""
        try:
            # Fill phone number
            self._fill_phone_field()
            
            # Fill cover letter
            self._fill_cover_letter(cover_letter)
            
            # Handle common questions
            self._answer_common_questions()
            
            # Upload resume if needed
            self._handle_resume_upload()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling form step: {e}")
            return False
    
    def _fill_phone_field(self):
        """Fill phone number field if present."""
        phone_selectors = [
            "input[name*='phone']",
            "input[id*='phone']",
            "input[placeholder*='phone']",
            "input[aria-label*='phone']"
        ]
        
        for selector in phone_selectors:
            try:
                phone_field = safe_find_element(
                    self.driver, By.CSS_SELECTOR, selector, timeout=2, required=False
                )
                if phone_field and not phone_field.get_attribute('value'):
                    self._type_with_human_delay(phone_field, "+44 123 456 7890")
                    break
            except Exception:
                continue
    
    def _fill_cover_letter(self, cover_letter: str):
        """Fill cover letter field if present."""
        cover_letter_selectors = [
            "textarea[name*='cover']",
            "textarea[id*='cover']",
            "textarea[placeholder*='cover']",
            "textarea[aria-label*='cover']",
            ".jobs-easy-apply-form-section__grouping textarea"
        ]
        
        for selector in cover_letter_selectors:
            try:
                cover_field = safe_find_element(
                    self.driver, By.CSS_SELECTOR, selector, timeout=2, required=False
                )
                if cover_field and not cover_field.get_attribute('value'):
                    # Clear field and type cover letter
                    cover_field.clear()
                    self._type_with_human_delay(cover_field, cover_letter[:1000])  # Limit length
                    break
            except Exception:
                continue
    
    def _answer_common_questions(self):
        """Answer common application questions automatically."""
        # Common questions and their answers
        common_answers = {
            'authorized': 'Yes',
            'visa': 'Yes',
            'relocate': 'Yes',
            'notice': '2 weeks',
            'salary': '35000',
            'experience': 'Yes'
        }
        
        # Find all input fields and dropdowns
        try:
            # Handle text inputs
            text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            for input_field in text_inputs:
                label_text = self._get_field_label(input_field).lower()
                
                for keyword, answer in common_answers.items():
                    if keyword in label_text and not input_field.get_attribute('value'):
                        self._type_with_human_delay(input_field, answer)
                        break
            
            # Handle dropdowns
            dropdowns = self.driver.find_elements(By.TAG_NAME, "select")
            for dropdown in dropdowns:
                label_text = self._get_field_label(dropdown).lower()
                
                if 'authorized' in label_text or 'visa' in label_text:
                    select = Select(dropdown)
                    self._select_option_containing(select, 'yes')
                elif 'relocate' in label_text:
                    select = Select(dropdown)
                    self._select_option_containing(select, 'yes')
            
        except Exception as e:
            self.logger.debug(f"Error answering questions: {e}")
    
    def _get_field_label(self, element) -> str:
        """Get the label text for a form field."""
        try:
            # Try to find label by 'for' attribute
            field_id = element.get_attribute('id')
            if field_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                return label.text
        except:
            pass
        
        try:
            # Try to find nearby label
            parent = element.find_element(By.XPATH, "..")
            label = parent.find_element(By.TAG_NAME, "label")
            return label.text
        except:
            pass
        
        # Return placeholder or aria-label as fallback
        return (element.get_attribute('placeholder') or 
                element.get_attribute('aria-label') or '')
    
    def _select_option_containing(self, select_element, text: str):
        """Select an option that contains the specified text."""
        try:
            options = select_element.options
            for option in options:
                if text.lower() in option.text.lower():
                    select_element.select_by_visible_text(option.text)
                    break
        except Exception as e:
            self.logger.debug(f"Error selecting option: {e}")
    
    def _handle_resume_upload(self):
        """Handle resume upload if required."""
        try:
            upload_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            for upload_input in upload_inputs:
                if upload_input.is_displayed():
                    # You would upload your resume file here
                    # upload_input.send_keys("/path/to/your/resume.pdf")
                    pass
        except Exception as e:
            self.logger.debug(f"Resume upload handling: {e}")
    
    def _proceed_to_next_step(self) -> bool:
        """Click Next or Submit button to proceed."""
        next_button_selectors = [
            "//button[contains(text(), 'Next')]",
            "//button[contains(text(), 'Continue')]",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Send application')]",
            ".jobs-easy-apply-form-actions__action-container button[aria-label*='Continue']",
            ".jobs-easy-apply-form-actions__action-container button[aria-label*='Submit']"
        ]
        
        for selector in next_button_selectors:
            try:
                if selector.startswith("//"):
                    button = safe_find_element(
                        self.driver, By.XPATH, selector, timeout=3, required=False
                    )
                else:
                    button = safe_find_element(
                        self.driver, By.CSS_SELECTOR, selector, timeout=3, required=False
                    )
                
                if button and button.is_enabled():
                    button.click()
                    human_delay(2, 4)
                    return True
            except Exception:
                continue
        
        return False
    
    def _is_application_complete(self) -> bool:
        """Check if application has been submitted successfully."""
        completion_indicators = [
            "//h3[contains(text(), 'Application sent')]",
            "//h2[contains(text(), 'Your application was sent')]",
            ".jobs-easy-apply-content h3",
            "[data-test-modal-id='application-sent-confirmation']"
        ]
        
        for selector in completion_indicators:
            try:
                if selector.startswith("//"):
                    element = safe_find_element(
                        self.driver, By.XPATH, selector, timeout=2, required=False
                    )
                else:
                    element = safe_find_element(
                        self.driver, By.CSS_SELECTOR, selector, timeout=2, required=False
                    )
                
                if element:
                    return True
            except Exception:
                continue
        
        return False
    
    def _type_with_human_delay(self, element, text: str):
        """Type text with human-like delays between characters."""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random delay between keystrokes
    
    def close_browser(self):
        """Clean up browser resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("🔒 Browser closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
    
    def get_session_stats(self) -> Dict:
        """Get comprehensive session statistics."""
        session_duration = 0
        if self.session_stats['session_start_time']:
            session_duration = time.time() - self.session_stats['session_start_time']
        
        return {
            **self.session_stats,
            'session_duration_minutes': round(session_duration / 60, 2),
            'success_rate': (self.session_stats['applications_successful'] / 
                           max(1, self.session_stats['applications_attempted']) * 100),
            'applications_per_minute': (self.session_stats['applications_attempted'] / 
                                      max(1, session_duration / 60))
        }
