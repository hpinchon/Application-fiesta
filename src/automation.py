import time
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config.settings import Config
from src.utils import setup_logging, calculate_applications_today
from src.linkedin_scraper import LinkedInJobScraper
from src.resume_tailor import ResumeAITailor
from src.linkedin_automation import LinkedInApplicationBot
from src.application_manager import ApplicationTracker

class LinkedInAutomationController:
    """
    Production-ready controller for LinkedIn job application automation.
    Handles the complete workflow with robust error handling and monitoring.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging()
        self.is_running = False
        self.session_stats = {
            'session_start': None,
            'jobs_discovered': 0,
            'jobs_analyzed': 0,
            'applications_attempted': 0,
            'applications_successful': 0,
            'errors_encountered': 0
        }
        
        # Initialize components
        self.scraper = None
        self.tailor = None
        self.automation_bot = None
        self.tracker = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"🛑 Received signal {signum}. Initiating graceful shutdown...")
        self.is_running = False
    
    def initialize_components(self) -> bool:
        """Initialize all automation components with error handling."""
        try:
            self.logger.info("🔧 Initializing automation components...")
            
            # Initialize job scraper
            self.scraper = LinkedInJobScraper()
            self.logger.info("✅ Job scraper initialized")
            
            # Initialize resume tailor
            self.tailor = ResumeAITailor()
            self.logger.info("✅ Resume tailor initialized")
            
            # Initialize application tracker
            self.tracker = ApplicationTracker()
            self.logger.info("✅ Application tracker initialized")
            
            # Initialize automation bot
            self.automation_bot = LinkedInApplicationBot()
            self.logger.info("✅ Automation bot initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            return False
    
    def run_daily_automation(self) -> Dict:
        """
        Execute the complete daily automation workflow.
        Returns comprehensive session statistics.
        """
        self.session_stats['session_start'] = datetime.now()
        self.is_running = True
        
        try:
            self.logger.info("🚀 Starting Daily LinkedIn Automation Workflow")
            
            # Step 1: Pre-flight checks
            if not self._perform_preflight_checks():
                return self._generate_session_report(success=False, reason="Pre-flight checks failed")
            
            # Step 2: Initialize components
            if not self.initialize_components():
                return self._generate_session_report(success=False, reason="Component initialization failed")
            
            # Step 3: Job discovery
            discovered_jobs = self._execute_job_discovery()
            if discovered_jobs.empty:
                return self._generate_session_report(success=True, reason="No jobs found matching criteria")
            
            # Step 4: Job analysis and filtering
            qualified_jobs = self._analyze_and_filter_jobs(discovered_jobs)
            if not qualified_jobs:
                return self._generate_session_report(success=True, reason="No qualified jobs after analysis")
            
            # Step 5: Browser automation and applications
            application_results = self._execute_applications(qualified_jobs)
            
            # Step 6: Generate final report
            return self._generate_session_report(success=True, application_results=application_results)
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Automation interrupted by user")
            return self._generate_session_report(success=False, reason="User interruption")
        except Exception as e:
            self.logger.error(f"❌ Automation workflow failed: {e}")
            self.session_stats['errors_encountered'] += 1
            return self._generate_session_report(success=False, reason=f"Unexpected error: {str(e)}")
        finally:
            self._cleanup_resources()
    
    def _perform_preflight_checks(self) -> bool:
        """Perform comprehensive pre-flight checks."""
        self.logger.info("🔍 Performing pre-flight checks...")
        
        try:
            # Check daily application limits
            applications_csv = f"{self.config.DATA_DIR}/applications.csv"
            today_count = calculate_applications_today(applications_csv)
            
            if today_count >= self.config.MAX_APPLICATIONS_PER_DAY:
                self.logger.warning(f"⚠️ Daily limit reached: {today_count}/{self.config.MAX_APPLICATIONS_PER_DAY}")
                return False
            
            # Check configuration validity
            if not self.config.DEFAULT_KEYWORDS:
                self.logger.error("❌ No job keywords configured")
                return False
            
            if not self.config.LINKEDIN_EMAIL or not self.config.LINKEDIN_PASSWORD:
                self.logger.error("❌ LinkedIn credentials not configured")
                return False
            
            # Check internet connectivity
            if not self._check_internet_connectivity():
                self.logger.error("❌ No internet connectivity")
                return False
            
            remaining_applications = self.config.MAX_APPLICATIONS_PER_DAY - today_count
            self.logger.info(f"✅ Pre-flight checks passed. Applications remaining: {remaining_applications}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Pre-flight check error: {e}")
            return False
    
    def _check_internet_connectivity(self) -> bool:
        """Check internet connectivity."""
        try:
            import requests
            response = requests.get("https://www.linkedin.com", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _execute_job_discovery(self):
        """Execute job discovery with error handling."""
        try:
            self.logger.info("🔍 Phase 1: Job Discovery")
            discovered_jobs = self.scraper.search_all_combinations()
            
            self.session_stats['jobs_discovered'] = len(discovered_jobs)
            self.logger.info(f"✅ Discovered {len(discovered_jobs)} jobs")
            
            return discovered_jobs
            
        except Exception as e:
            self.logger.error(f"❌ Job discovery failed: {e}")
            self.session_stats['errors_encountered'] += 1
            raise
    
    def _analyze_and_filter_jobs(self, discovered_jobs) -> List[Dict]:
        """Analyze jobs and filter for qualified applications."""
        try:
            self.logger.info("🎯 Phase 2: Job Analysis and Filtering")
            qualified_jobs = []
            
            for idx, job_row in discovered_jobs.iterrows():
                if not self.is_running:  # Check for shutdown signal
                    break
                
                job_data = job_row.to_dict()
                
                # Skip if already applied
                if self.tracker.check_already_applied(job_data.get('job_url', '')):
                    continue
                
                # Analyze job fit
                analysis = self.tailor.analyze_application_fit(job_data)
                self.session_stats['jobs_analyzed'] += 1
                
                # Filter qualified jobs
                if analysis['should_apply'] and analysis['priority_score'] > 0.6:
                    job_data.update(analysis)
                    qualified_jobs.append(job_data)
            
            # Sort by priority and limit to daily quota
            qualified_jobs.sort(key=lambda x: x['priority_score'], reverse=True)
            
            # Limit to remaining daily applications
            applications_csv = f"{self.config.DATA_DIR}/applications.csv"
            today_count = calculate_applications_today(applications_csv)
            remaining = self.config.MAX_APPLICATIONS_PER_DAY - today_count
            qualified_jobs = qualified_jobs[:remaining]
            
            self.logger.info(f"📈 Analysis complete: {len(qualified_jobs)} qualified jobs")
            return qualified_jobs
            
        except Exception as e:
            self.logger.error(f"❌ Job analysis failed: {e}")
            self.session_stats['errors_encountered'] += 1
            raise
    
    def _execute_applications(self, qualified_jobs: List[Dict]) -> Dict:
        """Execute automated job applications."""
        try:
            self.logger.info("🎯 Phase 3: Automated Applications")
            
            # Initialize browser
            if not self.automation_bot.initialize_browser():
                raise Exception("Browser initialization failed")
            
            # Login to LinkedIn
            if not self.automation_bot.login_to_linkedin():
                raise Exception("LinkedIn login failed")
            
            # Process applications
            successful_applications = 0
            failed_applications = 0
            
            for i, job in enumerate(qualified_jobs, 1):
                if not self.is_running:  # Check for shutdown signal
                    break
                
                self.logger.info(f"📝 Processing application {i}/{len(qualified_jobs)}: {job['company']} - {job['title']}")
                self.session_stats['applications_attempted'] += 1
                
                try:
                    # Apply to job
                    application_success = self.automation_bot.apply_to_job(
                        job, job['cover_letter']
                    )
                    
                    # Log application
                    status = 'Applied' if application_success else 'Failed'
                    self.tracker.log_application(job, job['similarity_score'], status)
                    
                    if application_success:
                        successful_applications += 1
                        self.session_stats['applications_successful'] += 1
                        self.logger.info(f"✅ Application {i} successful")
                    else:
                        failed_applications += 1
                        self.logger.warning(f"❌ Application {i} failed")
                    
                    # Human-like delay between applications
                    if i < len(qualified_jobs) and self.is_running:
                        delay_time = self.config.DELAY_BETWEEN_APPLICATIONS
                        self.logger.info(f"⏳ Waiting {delay_time} seconds...")
                        time.sleep(delay_time)
                
                except Exception as e:
                    self.logger.error(f"❌ Application {i} error: {e}")
                    self.tracker.log_application(job, job['similarity_score'], 'Error')
                    failed_applications += 1
                    self.session_stats['errors_encountered'] += 1
                    continue
            
            return {
                'total_attempted': len(qualified_jobs),
                'successful': successful_applications,
                'failed': failed_applications,
                'success_rate': (successful_applications / max(1, len(qualified_jobs))) * 100
            }
            
        except Exception as e:
            self.logger.error(f"❌ Application execution failed: {e}")
            self.session_stats['errors_encountered'] += 1
            raise
    
    def _generate_session_report(self, success: bool, reason: str = None, application_results: Dict = None) -> Dict:
        """Generate comprehensive session report."""
        session_duration = 0
        if self.session_stats['session_start']:
            session_duration = (datetime.now() - self.session_stats['session_start']).total_seconds() / 60
        
        report = {
            'session_success': success,
            'session_duration_minutes': round(session_duration, 2),
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'statistics': {
                **self.session_stats,
                'session_duration_minutes': round(session_duration, 2)
            }
        }
        
        if application_results:
            report['application_results'] = application_results
        
        # Log summary
        self.logger.info("📊 Session Summary:")
        self.logger.info(f"   - Success: {success}")
        self.logger.info(f"   - Duration: {session_duration:.1f} minutes")
        self.logger.info(f"   - Jobs discovered: {self.session_stats['jobs_discovered']}")
        self.logger.info(f"   - Jobs analyzed: {self.session_stats['jobs_analyzed']}")
        self.logger.info(f"   - Applications attempted: {self.session_stats['applications_attempted']}")
        self.logger.info(f"   - Applications successful: {self.session_stats['applications_successful']}")
        
        if application_results:
            self.logger.info(f"   - Success rate: {application_results['success_rate']:.1f}%")
        
        return report
    
    def _cleanup_resources(self):
        """Clean up resources and close connections."""
        try:
            if self.automation_bot:
                self.automation_bot.close_browser()
            self.logger.info("🧹 Resources cleaned up successfully")
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")
