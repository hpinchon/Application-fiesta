#!/usr/bin/env python3
"""Test script for the resume tailoring system"""

import sys
import os
from src.utils import setup_logging
from src.resume_tailor import ResumeAITailor

def test_resume_tailor():
    """Test the resume tailoring functionality with sample job data"""
    
    # Set up logging
    logger = setup_logging()
    
    try:
        logger.info("=== Testing Resume Tailoring System ===")
        
        # Initialize the tailor
        tailor = ResumeAITailor()
        
        # Sample job data for testing
        sample_job = {
            'title': 'Data Analyst',
            'company': 'TechCorp Solutions',
            'location': 'London, UK',
            'description': '''
            We are seeking a skilled Data Analyst to join our growing team. 
            The ideal candidate will have experience with Python, SQL, and data visualization tools like Tableau.
            
            Key Requirements:
            - 2-3 years of experience in data analysis
            - Proficiency in Python and SQL
            - Experience with Tableau or Power BI
            - Strong analytical and problem-solving skills
            - Excellent communication skills
            - Bachelor's degree in relevant field
            
            We offer a collaborative work environment, opportunities for growth, 
            and the chance to work on innovative projects that impact our business.
            '''
        }
        
        logger.info(f"Testing with sample job: {sample_job['title']} at {sample_job['company']}")
        
        # Test requirement extraction
        logger.info("Testing requirement extraction...")
        requirements = tailor.extract_job_requirements(sample_job['description'])
        
        logger.info(f"✅ Extracted {len(requirements['skills'])} relevant skills")
        logger.info(f"✅ Experience level detected: {requirements['experience_level']}")
        logger.info(f"✅ Key phrases found: {len(requirements['key_phrases'])}")
        
        # Test similarity calculation
        logger.info("Testing similarity calculation...")
        similarity = tailor.calculate_resume_job_similarity(sample_job['description'])
        logger.info(f"✅ Resume-job similarity: {similarity:.3f}")
        
        # Test full analysis
        logger.info("Testing comprehensive application analysis...")
        analysis = tailor.analyze_application_fit(sample_job)
        
        logger.info(f"✅ Analysis completed:")
        logger.info(f"   - Similarity Score: {analysis['similarity_score']:.3f}")
        logger.info(f"   - Priority Score: {analysis['priority_score']:.3f}")
        logger.info(f"   - Should Apply: {analysis['should_apply']}")
        logger.info(f"   - Recommendations: {len(analysis['recommendations'])}")
        
        # Test cover letter generation
        logger.info("Testing cover letter generation...")
        cover_letter = analysis['cover_letter']
        
        if len(cover_letter) > 100:
            logger.info("✅ Cover letter generated successfully")
            logger.info(f"Cover letter preview: {cover_letter[:150]}...")
        else:
            logger.warning("⚠️ Cover letter seems too short")
        
        # Display sample results
        logger.info("\n=== Sample Analysis Results ===")
        logger.info(f"Top Skills Required:")
        for skill in requirements['skills'][:5]:
            logger.info(f"  - {skill['skill']} ({skill['category']})")
        
        logger.info(f"\nRecommendations:")
        for rec in analysis['recommendations']:
            logger.info(f"  - {rec}")
        
        logger.info("🎉 Resume tailoring system test completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_resume_tailor()
    if not success:
        sys.exit(1)
