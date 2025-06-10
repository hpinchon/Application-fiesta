import pandas as pd
import os
from datetime import datetime

class ApplicationTracker:
    def __init__(self, csv_path='data/applications.csv'):
        self.csv_path = csv_path
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """
        Create CSV file with headers if it doesn't exist
        """
        if not os.path.exists(self.csv_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            
            # Create empty DataFrame with required columns
            columns = [
                'application_date', 'company', 'position', 'location', 'job_url',
                'similarity_score', 'application_status', 'platform', 'job_type',
                'salary_range', 'description_snippet', 'key_skills', 'notes',
                'follow_up_date', 'response_received', 'interview_scheduled'
            ]
            
            empty_df = pd.DataFrame(columns=columns)
            empty_df.to_csv(self.csv_path, index=False)
    
    def log_application(self, job_data, similarity_score, status='Applied'):
        """
        Log a new job application to the CSV file
        """
        try:
            # Prepare application record
            application_record = {
                'application_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'company': job_data.get('company', 'Unknown'),
                'position': job_data.get('title', 'Unknown'),
                'location': job_data.get('location', 'Unknown'),
                'job_url': job_data.get('job_url', ''),
                'similarity_score': round(similarity_score, 3),
                'application_status': status,
                'platform': 'LinkedIn',
                'job_type': job_data.get('job_type', 'Unknown'),
                'salary_range': job_data.get('compensation', 'Not specified'),
                'description_snippet': str(job_data.get('description', ''))[:200] + '...',
                'key_skills': ', '.join(job_data.get('extracted_skills', [])),
                'notes': '',
                'follow_up_date': '',
                'response_received': 'No',
                'interview_scheduled': 'No'
            }
            
            # Read existing data
            df = pd.read_csv(self.csv_path)
            
            # Add new record
            new_row = pd.DataFrame([application_record])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save updated data
            df.to_csv(self.csv_path, index=False)
            
            print(f"✅ Logged application: {application_record['company']} - {application_record['position']}")
            
        except Exception as e:
            print(f"Error logging application: {e}")
    
    def check_already_applied(self, job_url):
        """
        Check if we've already applied to this job
        """
        try:
            df = pd.read_csv(self.csv_path)
            return job_url in df['job_url'].values
        except:
            return False
    
    def get_application_stats(self):
        """
        Get summary statistics of applications
        """
        try:
            df = pd.read_csv(self.csv_path)
            
            if df.empty:
                return "No applications logged yet."
            
            stats = {
                'total_applications': len(df),
                'applications_today': len(df[df['application_date'].str.contains(datetime.now().strftime('%Y-%m-%d'))]),
                'avg_similarity_score': df['similarity_score'].mean(),
                'top_companies': df['company'].value_counts().head(5).to_dict(),
                'response_rate': (df['response_received'] == 'Yes').sum() / len(df) * 100
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
