import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from jobspy import scrape_jobs
from config.settings import Config
from src.utils import human_delay, clean_text

class LinkedInJobScraper:
    """
    Advanced LinkedIn job discovery engine that finds relevant opportunities
    while respecting rate limits and avoiding detection.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('LinkedInAutomation')
        self.scraped_jobs = pd.DataFrame()
        self.search_stats = {
            'total_searches': 0,
            'total_jobs_found': 0,
            'jobs_after_filtering': 0,
            'search_start_time': None
        }
    
    def scrape_jobs_batch(self, search_term: str, location: str, max_results: int = 100) -> pd.DataFrame:
        """
        Scrape jobs using JobSpy with error handling and rate limiting.
        JobSpy is more efficient and less likely to trigger anti-bot measures.
        """
        self.logger.info(f"🔍 Searching: '{search_term}' in '{location}'")
        
        try:
            # Use JobSpy for efficient scraping
            jobs_df = scrape_jobs(
                site_name=["linkedin"],
                search_term=search_term,
                location=location,
                results_wanted=max_results,
                hours_old=24,  # Only recent jobs
                country_indeed='UK',  # Adjust based on your location
                linkedin_fetch_description=True,  # Get full descriptions
                linkedin_company_ids=None  # Can target specific companies
            )
            
            if not jobs_df.empty:
                # Add metadata for tracking
                jobs_df['scraped_at'] = datetime.now()
                jobs_df['search_term'] = search_term
                jobs_df['search_location'] = location
                jobs_df['source_platform'] = 'LinkedIn'
                
                self.logger.info(f"✅ Found {len(jobs_df)} jobs for '{search_term}'")
                self.search_stats['total_jobs_found'] += len(jobs_df)
                
                return jobs_df
            else:
                self.logger.warning(f"⚠️ No jobs found for '{search_term}' in '{location}'")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"❌ Error scraping jobs for '{search_term}': {str(e)}")
            return pd.DataFrame()
    
    def filter_jobs_by_criteria(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply intelligent filtering based on job preferences and requirements.
        This ensures we only process relevant opportunities.
        """
        if jobs_df.empty:
            return jobs_df
        
        original_count = len(jobs_df)
        filtered_jobs = jobs_df.copy()
        
        # Filter 1: Remove jobs without descriptions (usually incomplete postings)
       # if 'description' in filtered_jobs.columns:
             #filtered_jobs = filtered_jobs[filtered_jobs['description'].notna()]
            #filtered_jobs = filtered_jobs[filtered_jobs['description'].str.len() > 10]
        
        # Filter 2: Job type filtering
        #job_config = self.config.job_search_config
       # if 'job_type' in filtered_jobs.columns and job_config['job_types']:
           # filtered_jobs = filtered_jobs[
                #filtered_jobs['job_type'].isin(job_config['job_types'])
          #  ]
        #
        # Filter 3: Experience level filtering
        #if 'seniority_level' in filtered_jobs.columns and job_config['experience_levels']:
            #filtered_jobs = filtered_jobs[
                #filtered_jobs['seniority_level'].isin(job_config['experience_levels'])
           # ]
        
        # Filter 4: Remove jobs with suspicious characteristics
        # Filter out jobs with very short titles (likely spam)
       # if 'title' in filtered_jobs.columns:
           # filtered_jobs = filtered_jobs[filtered_jobs['title'].str.len() >= 6]
        
        # Filter 5: Easy Apply preference
      #  if job_config['easy_apply_only']:
            # JobSpy marks easy apply jobs - adjust based on actual column structure
            #if 'emails' in filtered_jobs.columns:
                # Jobs with emails usually require external application
              #  filtered_jobs = filtered_jobs[filtered_jobs['emails'].isna()]
        
        filtered_count = len(filtered_jobs)
        self.logger.info(f"📊 Filtered: {original_count} → {filtered_count} jobs ({filtered_count/original_count*100:.1f}% kept)")
        
        return filtered_jobs
    
    def remove_duplicates(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate job postings based on multiple criteria.
        Companies often post the same job multiple times.
        """
        if jobs_df.empty:
            return jobs_df
        
        original_count = len(jobs_df)
        
        # Remove duplicates based on job URL (most reliable)
        if 'job_url' in jobs_df.columns:
            jobs_df = jobs_df.drop_duplicates(subset=['job_url'], keep='first')
        
        # Remove duplicates based on company + title combination
        if 'company' in jobs_df.columns and 'title' in jobs_df.columns:
            jobs_df = jobs_df.drop_duplicates(subset=['company', 'title'], keep='first')
        
        dedupe_count = len(jobs_df)
        if dedupe_count < original_count:
            self.logger.info(f"🔄 Removed {original_count - dedupe_count} duplicate jobs")
        
        return jobs_df
    
    def search_all_combinations(self) -> pd.DataFrame:
        """
        Execute comprehensive job search across all keyword and location combinations.
        This is the main orchestration method for job discovery.
        """
        self.search_stats['search_start_time'] = datetime.now()
        job_config = self.config.job_search_config
        all_jobs = []
        
        self.logger.info(f"🚀 Starting job search with {len(job_config['keywords'])} keywords and {len(job_config['locations'])} locations")
        
        for keyword in job_config['keywords']:
            for location in job_config['locations']:
                # Search for jobs
                jobs_batch = self.scrape_jobs_batch(keyword, location, max_results=150)
                
                if not jobs_batch.empty:
                    # Apply filtering
                    filtered_jobs = self.filter_jobs_by_criteria(jobs_batch)
                    
                    if not filtered_jobs.empty:
                        all_jobs.append(filtered_jobs)
                
                # Rate limiting to be respectful to LinkedIn's servers
                human_delay(3, 7)  # Wait 3-7 seconds between searches
                self.search_stats['total_searches'] += 1
        
        # Combine all results
        if all_jobs:
            combined_jobs = pd.concat(all_jobs, ignore_index=True)
            
            # Remove duplicates across all searches
            final_jobs = self.remove_duplicates(combined_jobs)
            
            # Store results
            self.scraped_jobs = final_jobs
            self.search_stats['jobs_after_filtering'] = len(final_jobs)
            
            # Log final statistics
            search_duration = datetime.now() - self.search_stats['search_start_time']
            self.logger.info(f"🎯 Search completed in {search_duration.total_seconds():.1f}s")
            self.logger.info(f"📈 Final results: {len(final_jobs)} unique, relevant jobs found")
            
            return final_jobs
        else:
            self.logger.warning("⚠️ No jobs found matching your criteria")
            return pd.DataFrame()
    
    def get_job_by_url(self, job_url: str) -> Optional[Dict]:
        """
        Retrieve a specific job by its URL from scraped results.
        Useful for application processing.
        """
        if self.scraped_jobs.empty:
            return None
        
        matching_jobs = self.scraped_jobs[self.scraped_jobs['job_url'] == job_url]
        if not matching_jobs.empty:
            return matching_jobs.iloc[0].to_dict()
        
        return None
    
    def get_search_statistics(self) -> Dict:
        """
        Return comprehensive search statistics for monitoring and optimization.
        """
        return {
            **self.search_stats,
            'jobs_per_search': self.search_stats['total_jobs_found'] / max(1, self.search_stats['total_searches']),
            'filter_efficiency': self.search_stats['jobs_after_filtering'] / max(1, self.search_stats['total_jobs_found']) * 100,
            'total_unique_jobs': len(self.scraped_jobs)
        }
    
    def export_jobs_to_csv(self, filename: Optional[str] = None) -> str:
        """
        Export discovered jobs to CSV for manual review and backup.
        """
        if self.scraped_jobs.empty:
            self.logger.warning("No jobs to export")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"discovered_jobs_{timestamp}.csv"
        
        filepath = f"{self.config.DATA_DIR}/{filename}"
        
        # Select relevant columns for export
        export_columns = [
            'title', 'company', 'location', 'job_type', 'date_posted',
            'job_url', 'description', 'salary_range', 'seniority_level',
            'scraped_at', 'search_term'
        ]
        
        # Only include columns that exist
        available_columns = [col for col in export_columns if col in self.scraped_jobs.columns]
        export_df = self.scraped_jobs[available_columns]
        
        export_df.to_csv(filepath, index=False)
        self.logger.info(f"💾 Exported {len(export_df)} jobs to {filepath}")
        
        return filepath
