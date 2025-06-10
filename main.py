#!/usr/bin/env python3
"""
LinkedIn Job Application Automation Tool
Complete automation pipeline with job discovery, tailoring, and application submission
"""

import sys
import os
import time
from src.utils import setup_logging, calculate_applications_today
from src.linkedin_scraper import LinkedInJobScraper
from src.resume_tailor import ResumeAITailor
from src.linkedin_automation import LinkedInApplicationBot
from src.application_manager import ApplicationTracker
from config.settings import Config

def main():
    """Main application entry point with complete automation pipeline"""
    
    # Initialize components
    config = Config()
    logger = setup_logging()
    
    try:
        logger.info("🚀 Starting Complete LinkedIn Job Application Automation")
        
        # Check daily limits
        applications_csv = os.path.join(config.DATA_DIR, 'applications.csv')
        today_count = calculate_applications_today(applications_csv)
        
        if today_count >= config.MAX_APPLICATIONS_PER_DAY:
            logger.warning(f"⚠️ Daily limit reached: {today_count}/{config.MAX_APPLICATIONS_PER_DAY}")
            return
        
        remaining_applications = config.MAX_APPLICATIONS_PER_DAY - today_count
        logger.info(f"📊 Applications remaining today: {remaining_applications}")
        
        # Initialize all components
        logger.info("🔧 Initializing automation components...")
        scraper = LinkedInJobScraper()
        tailor = ResumeAITailor()
        automation_bot = LinkedInApplicationBot()
        tracker = ApplicationTracker()
        
        # Step 1: Discover jobs
        logger.info("🔍 Phase 1: Job Discovery")
        discovered_jobs = scraper.search_all_combinations()
        
        if discovered_jobs.empty:
            logger.warning("⚠️ No jobs found. Exiting.")
            return
        
        logger.info(f"✅ Found {len(discovered_jobs)} jobs")
        
        # Step 2: Analyze and filter jobs
        logger.info("🎯 Phase 2: Job Analysis and Filtering")
        qualified_jobs = []
        
        for idx, job_row in discovered_jobs.iterrows():
            job_data = job_row.to_dict()
            
            # Skip if already applied
            if tracker.check_already_applied(job_data.get('job_url', '')):
                continue
            
            # Analyze job fit
            analysis = tailor.analyze_application_fit(job_data)
            
            if analysis['should_apply'] and analysis['priority_score'] > 0.1:
                job_data.update(analysis)
                qualified_jobs.append(job_data)
        
        # Sort by priority score
        qualified_jobs.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Limit to remaining daily applications
        qualified_jobs = qualified_jobs[:remaining_applications]
        
        logger.info(f"📈 Qualified jobs for application: {len(qualified_jobs)}")
        
        if not qualified_jobs:
            logger.info("ℹ️ No qualified jobs found for application")
            return
        
        # Step 3: Initialize browser and login
        logger.info("🌐 Phase 3: Browser Initialization and Login")
        if not automation_bot.initialize_browser():
            logger.error("❌ Failed to initialize browser")
            return
        
        if not automation_bot.login_to_linkedin():
            logger.error("❌ Failed to login to LinkedIn")
            automation_bot.close_browser()
            return
        
        # Step 4: Apply to jobs
        logger.info("🎯 Phase 4: Automated Job Applications")
        successful_applications = 0
        
        for i, job in enumerate(qualified_jobs, 1):
            logger.info(f"📝 Processing application {i}/{len(qualified_jobs)}")
            
            try:
                # Apply to job
                application_success = automation_bot.apply_to_job(
                    job, job['cover_letter']
                )
                
                # Log application attempt
                status = 'Applied' if application_success else 'Failed'
                tracker.log_application(job, job['similarity_score'], status)
                
                if application_success:
                    successful_applications += 1
                    logger.info(f"✅ Application {i} successful: {job['company']} - {job['title']}")
                else:
                    logger.warning(f"❌ Application {i} failed: {job['company']} - {job['title']}")
                
                # Human-like delay between applications
                if i < len(qualified_jobs):  # Don't delay after last application
                    delay_time = config.DELAY_BETWEEN_APPLICATIONS
                    logger.info(f"⏳ Waiting {delay_time} seconds before next application...")
                    time.sleep(delay_time)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Application process interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Error processing application {i}: {e}")
                tracker.log_application(job, job['similarity_score'], 'Error')
                continue
        
        # Step 5: Session summary
        logger.info("📊 Phase 5: Session Summary")
        session_stats = automation_bot.get_session_stats()
        app_stats = tracker.get_application_stats()
        
        logger.info(f"🎉 Automation session completed!")
        logger.info(f"📈 Session Statistics:")
        logger.info(f"   - Applications attempted: {session_stats['applications_attempted']}")
        logger.info(f"   - Applications successful: {session_stats['applications_successful']}")
        logger.info(f"   - Success rate: {session_stats['success_rate']:.1f}%")
        logger.info(f"   - Session duration: {session_stats['session_duration_minutes']:.1f} minutes")
        
        if isinstance(app_stats, dict):
            logger.info(f"📋 Total Applications Today: {app_stats.get('applications_today', 0)}")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Application interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise
    finally:
        # Clean up
        try:
            automation_bot.close_browser()
        except:
            pass
        logger.info("=== LinkedIn Automation Session Ended ===")

if __name__ == "__main__":
    main()
