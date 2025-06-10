import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from config.settings import Config

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class ResumeAITailor:
    """
    Advanced AI-powered resume and cover letter tailoring system.
    Analyzes job descriptions and customizes application materials for maximum impact.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('LinkedInAutomation')
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2),  # Include bigrams for better context
            min_df=1,
            max_df=0.95
        )
        
        # Load your base resume content
        self.base_resume_text = self.load_base_resume()
        self.skill_keywords = self.load_skill_database()
        
    def load_base_resume(self) -> str:
        """
        Load your base resume content for similarity matching.
        In production, this would read from your actual resume file.
        """
        # This should be replaced with your actual resume content
        base_resume = """
        
EDUCATION

The London School of Economics and Political Science, UK	Sep 2024 - Sep 2025
Master’s Degree in Political Economy (Expected Grade: Distinction)
•	Relevant Courses: Advanced Econometrics, Political Science and Political Economy, Game Theory, Politics of Money, Financial Markets, European Monetary Integration, R Studio

University Paris II Panthéon-Assas, FR	Sep 2021 – Sep 2024
Bachelor of Economics and Management, 2:1 (Graduated among the top 5%)
•	Relevant Courses: Econometrics, Statistics, Applied Mathematics, Advanced Macroeconomics, Financial Economics, Microeconomics, Geoeconomics, Accounting, Financial Analysis, VBA, Stata, Python

WORK EXPERIENCE

The Macro Newsletter, London, UK		May 2025 -
Researcher and Editor
•	Founder and editor of a monthly macroeconomic newsletter. https://hugopinchon.substack.com
•	Conducted in-depth analysis of global macroeconomic trends and policies, and analysed financial markets dynamics.
•	Explored topics such as international trade, debt sustainability, financial stability, economic growth and monetary policies.
•	Wrote clear and concise reports on complex economic issues, tailored for non-professional readers and enhanced abilities to translate complex concepts into accessible content.
•	Improved analytical and writing skills through regular economic reporting and strengthened understanding of global economic trends and their impact.
Globalong, Phnom Penh, Cambodia	July 2024 – July 2024
Public Affairs Consultant
•	Participated in a volunteer program focused on public affairs management in Cambodia.
•	Performed comprehensive analysis and documentation of governance laws and guidelines, formulating innovative best practice strategies to strengthen compliance, transparency, and organisational efficiency.
•	Conducted in-depth assessments of economic policies, analysing their design, implementation, and measurable impact to provide actionable insights and strategic recommendations for enhanced effectiveness.
•	Collaborated with the local public to optimise resource allocation, improve financial management, and implement strategies that enhanced economic efficiency.
The Sneakers shop, France	Jan 2019 – Sep 2024
Founder and Operator
•	Launched and operated an online sneaker resale business, achieving over £20k per year in revenue through strategic buying.
•	Conducted thorough market research and price analysis to identify profitable opportunities, driving a consistent profit margin by capitalising on demand fluctuations.
•	Managed all financial aspects of the business, including budgeting, cost control, and cash flow management.

EXTRA-CURRICULAR ACTIVITIES
Member of the UCA’s Finance Club	Sep 2022 - June 2023
•	Led research and analysis on financial markets and trends, contributing to the club’s newsletter and presentations on market outlooks, investment strategies, and economic policy impacts.
•	Engaged in debates and discussions on macroeconomic trends, sharpening critical thinking and market analysis skills relevant to finance roles.
Academic Research	2021 - 2025
•	Quantitative and qualitative research using modelling and data analysis tools (R, Python) and application of game theory to model complex economic and political scenarios. 
•	Conducted economics and political science research using econometric models; “The Incidence of weak economic and political institutions on the occurrence of sovereign debt distress in heavily indebted poor countries”, “Populist Movements and LGBT rights: an empirical analysis of political trends”.
•	Subjects of interest: political economy of development, development economics, development finance, sovereign debt management, tech economics, economics of AI, issues linked to the development of space economics.

SKILLS

Languages: English (fluent, IELTS 7.5/9), French (Native), Chinese (Beginner), Italian (Beginner)
IT Skills: MS Office, Excel, PowerPoint, VBA, Python (Beginner), R (Advanced)


        """
        
        self.logger.info("Base resume content loaded for similarity matching")
        return base_resume
    
    def load_skill_database(self) -> Dict[str, List[str]]:
        """
        Comprehensive skill database organized by categories.
        This helps identify relevant skills from job descriptions.
        """
        return {
            'programming': [
                'python', 'r', 
            ],
            'economics': [
                'econometrics', 'difference-in-differences', 'did regression', 'causal inference',
            'instrumental variables', 'regression discontinuity', 'panel data analysis',
            'time series analysis', 'forecasting', 'economic modeling', 'stata', 'eviews',
            'monetary policy', 'fiscal policy', 'macroeconomics', 'microeconomics',
            'gdp analysis', 'inflation modeling', 'economic growth', 'market analysis',
            'financial economics', 'behavioral economics', 'development economics',
            'international economics', 'labor economics', 'public economics',
            'game theory', 'optimization', 'cost-benefit analysis', 'policy analysis',
            'economic research', 'quantitative economics', 'applied economics'
            ],
            'statistics': [
                'statistical analysis', 'hypothesis testing', 'p-values', 'confidence intervals',
            'normal distribution', 'regression analysis', 'anova', 'chi-square test',
            't-test', 'correlation analysis', 'multivariate analysis', 'bayesian statistics',
            'non-parametric statistics', 'survival analysis', 'factor analysis',
            'cluster analysis', 'monte carlo simulation', 'bootstrap methods',
            'statistical modeling', 'experimental design', 'a/b testing',
            'statistical inference', 'descriptive statistics', 'probability theory',
            'stochastic processes', 'statistical software'
            ],
            'finance': [
                'financial modeling', 'valuation', 'dcf analysis', 'financial statements',
            'ratio analysis', 'risk management', 'portfolio optimization', 'derivatives',
            'fixed income', 'equity analysis', 'credit analysis', 'financial planning',
            'budgeting', 'forecasting', 'variance analysis', 'cost accounting',
            'management accounting', 'financial reporting', 'audit', 'compliance',
            'bloomberg terminal', 'reuters', 'factset', 'capital markets',
            'investment banking', 'corporate finance', 'quantitative finance'
            ],
            'business_tools': [
                'excel', 'tableau'
            ],
            'macro_research_methodologies': [
                'time series analysis', 'vector autoregression', 'VAR models',
            'structural equation modeling', 'dynamic stochastic general equilibrium',
            'DSGE models', 'panel data econometrics', 'cointegration analysis',
            'error correction models', 'macroeconomic forecasting', 'bayesian econometrics',
            'state space models', 'kalman filter', 'impulse response functions',
            'spectral analysis', 'nonlinear time series', 'HAC estimators',
            'heteroskedasticity and autocorrelation consistent', 'macroeconomic policy analysis',
            'macroeconomic modeling', 'growth accounting', 'business cycle analysis',
            'monetary policy analysis', 'fiscal policy evaluation', 'macroeconomic data analysis',
            'structural breaks', 'panel cointegration', 'unit root tests',
            'macroeconometrics', 'granger causality', 'johansen cointegration',
            'arch models', 'garch models', 'volatility modeling'
            ]
        }
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, any]:
        """
        Extract key requirements and information from job description using NLP.
        This creates a structured analysis of what the employer is looking for.
        """
        if not job_description or pd.isna(job_description):
            return {'skills': [], 'experience_level': 'unknown', 'key_phrases': []}
        
        # Clean and normalize text
        clean_desc = self.clean_text(job_description.lower())
        
        # Extract skills mentioned in the job description
        found_skills = []
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                if skill in clean_desc:
                    found_skills.append({
                        'skill': skill,
                        'category': category,
                        'frequency': clean_desc.count(skill)
                    })
        
        # Sort skills by frequency (most mentioned first)
        found_skills.sort(key=lambda x: x['frequency'], reverse=True)
        
        # Extract experience level indicators
        experience_level = self.extract_experience_level(clean_desc)
        
        # Extract key phrases using TF-IDF
        key_phrases = self.extract_key_phrases(clean_desc)
        
        # Extract company values and culture keywords
        culture_keywords = self.extract_culture_keywords(clean_desc)
        
        return {
            'skills': found_skills[:15],  # Top 15 most relevant skills
            'experience_level': experience_level,
            'key_phrases': key_phrases[:10],  # Top 10 key phrases
            'culture_keywords': culture_keywords,
            'word_count': len(clean_desc.split()),
            'complexity_score': self.calculate_complexity_score(clean_desc)
        }
    
    def extract_experience_level(self, job_text: str) -> str:
        """Determine the experience level required for the position."""
        experience_patterns = {
            'entry': ['entry level', 'junior', 'graduate', 'new grad', '0-2 years', 'recent graduate'],
            'mid': ['mid level', 'intermediate', '2-5 years', '3-7 years', 'experienced'],
            'senior': ['senior', 'lead', 'principal', '5+ years', '7+ years', 'expert', 'advanced'],
            'executive': ['director', 'manager', 'head of', 'vp', 'vice president', 'chief', 'executive']
        }
        
        for level, patterns in experience_patterns.items():
            if any(pattern in job_text for pattern in patterns):
                return level
        
        return 'entry'  # Default assumption
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract important phrases using TF-IDF analysis."""
        try:
            # Create a simple corpus for TF-IDF
            corpus = [text, self.base_resume_text]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Get feature names and scores for the job description
            feature_names = self.vectorizer.get_feature_names_out()
            job_scores = tfidf_matrix[0].toarray()[0]
            
            # Get top scoring phrases
            phrase_scores = list(zip(feature_names, job_scores))
            phrase_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top phrases with meaningful scores
            return [phrase for phrase, score in phrase_scores[:10] if score > 0.1]
        
        except Exception as e:
            self.logger.warning(f"Error extracting key phrases: {e}")
            return []
    
    def extract_culture_keywords(self, job_text: str) -> List[str]:
        """Extract company culture and value-related keywords."""
        culture_indicators = [
            'collaborative', 'innovative', 'fast-paced', 'dynamic', 'flexible',
            'remote', 'hybrid', 'team player', 'leadership', 'growth mindset',
            'diversity', 'inclusion', 'work-life balance', 'startup', 'enterprise'
        ]
        
        found_culture = [keyword for keyword in culture_indicators if keyword in job_text]
        return found_culture
    
    def calculate_complexity_score(self, text: str) -> float:
        """Calculate job complexity based on technical terms and requirements."""
        technical_terms = sum(1 for category in self.skill_keywords.values() 
                            for skill in category if skill in text)
        word_count = len(text.split())
        
        # Normalize complexity score (0-1 scale)
        complexity = min(technical_terms / max(word_count / 100, 1), 1.0)
        return round(complexity, 3)
    
    def calculate_resume_job_similarity(self, job_description: str) -> float:
        """
        Calculate similarity between your resume and the job description.
        Higher scores indicate better matches.
        """
        try:
            # Clean both texts
            resume_clean = self.clean_text(self.base_resume_text)
            job_clean = self.clean_text(job_description)
            
            # Calculate TF-IDF similarity
            documents = [resume_clean, job_clean]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            similarity_score = similarity_matrix[0][0]
            
            self.logger.debug(f"Resume-job similarity calculated: {similarity_score:.3f}")
            return round(similarity_score, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def generate_tailored_cover_letter(self, job_data: Dict, requirements: Dict) -> str:
        """
        Generate a personalized cover letter based on job requirements.
        Uses extracted skills and company information for customization.
        """
        try:
            # Extract basic job information
            company = job_data.get('company', 'the company')
            position = job_data.get('title', 'this position')
            location = job_data.get('location', '')
            
            # Get top skills for this job
            top_skills = [skill['skill'] for skill in requirements['skills'][:5]]
            skills_text = ', '.join(top_skills) if top_skills else 'relevant technologies'
            
            # Get culture keywords for personalization
            culture_keywords = requirements.get('culture_keywords', [])
            culture_text = self.generate_culture_paragraph(culture_keywords)
            
            # Generate experience-appropriate content
            experience_content = self.generate_experience_content(requirements['experience_level'])
            
            # Create the tailored cover letter
            cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {position} role at {company}. {experience_content}

Your job posting particularly caught my attention because of the opportunity to work with {skills_text}. My background aligns well with your requirements, and I am excited about the possibility of contributing to {company}'s continued success.

{culture_text}

I would welcome the opportunity to discuss how my skills and enthusiasm can benefit your team. Thank you for considering my application.

Best regards,
[Your Name]"""

            self.logger.info(f"Generated tailored cover letter for {company} - {position}")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}")
            return self.get_default_cover_letter(job_data)
    
    def generate_culture_paragraph(self, culture_keywords: List[str]) -> str:
        """Generate a paragraph that addresses company culture keywords."""
        if not culture_keywords:
            return "I am particularly drawn to your company's commitment to innovation and excellence."
        
        culture_responses = {
            'collaborative': "I thrive in collaborative environments and enjoy working with cross-functional teams.",
            'innovative': "I am passionate about innovation and bringing creative solutions to complex challenges.",
            'fast-paced': "I excel in fast-paced environments and adapt quickly to changing priorities.",
            'remote': "I have extensive experience working effectively in remote and distributed teams.",
            'growth mindset': "I embrace continuous learning and am always seeking opportunities to grow professionally."
        }
        
        # Select relevant responses
        relevant_responses = [culture_responses.get(keyword, '') for keyword in culture_keywords[:2]]
        relevant_responses = [resp for resp in relevant_responses if resp]
        
        if relevant_responses:
            return ' '.join(relevant_responses)
        else:
            return "I am excited about the opportunity to contribute to your team's success and grow within your organization."
    
    def generate_experience_content(self, experience_level: str) -> str:
        """Generate appropriate content based on experience level."""
        experience_content = {
            'entry': "As a recent graduate with a strong foundation in technology and analytics, I am eager to apply my skills in a professional environment.",
            'mid': "With several years of experience in data analysis and technology, I have developed strong skills in problem-solving and project execution.",
            'senior': "As an experienced professional with a proven track record in leadership and technical excellence, I am excited about taking on new challenges.",
            'executive': "With extensive leadership experience and a strategic mindset, I am well-positioned to drive organizational success."
        }
        
        return experience_content.get(experience_level, experience_content['entry'])
    
    def get_default_cover_letter(self, job_data: Dict) -> str:
        """Fallback cover letter template."""
        company = job_data.get('company', 'your company')
        position = job_data.get('title', 'this position')
        
        return f"""Dear Hiring Manager,

I am writing to express my interest in the {position} role at {company}. 
My background and skills align well with the requirements for this position.

I would welcome the opportunity to discuss how I can contribute to your team's success.

Best regards,
[Your Name]"""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for processing."""
        if not text or pd.isna(text):
            return ""
        
        # Convert to lowercase and remove special characters
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def analyze_application_fit(self, job_data: Dict) -> Dict[str, any]:
        """
        Comprehensive analysis of how well you fit the job requirements.
        Returns detailed metrics and recommendations.
        """
        job_description = job_data.get('description', '')
        
        # Extract job requirements
        requirements = self.extract_job_requirements(job_description)
        
        # Calculate similarity score
        similarity_score = self.calculate_resume_job_similarity(job_description)
        
        # Generate tailored cover letter
        cover_letter = self.generate_tailored_cover_letter(job_data, requirements)
        
        # Calculate application priority score
        priority_score = self.calculate_priority_score(requirements, similarity_score)
        
        # Generate application recommendations
        recommendations = self.generate_recommendations(requirements, similarity_score)
        
        analysis_result = {
            'similarity_score': similarity_score,
            'priority_score': priority_score,
            'requirements': requirements,
            'cover_letter': cover_letter,
            'recommendations': recommendations,
            'should_apply': similarity_score >= self.config.job_search_config['similarity_threshold'],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Application analysis completed - Similarity: {similarity_score:.3f}, Priority: {priority_score:.3f}")
        
        return analysis_result
    
    def calculate_priority_score(self, requirements: Dict, similarity_score: float) -> float:
        """Calculate priority score for application ranking."""
        base_score = similarity_score
        
        # Boost score for high-demand skills
        skill_boost = min(len(requirements['skills']) * 0.02, 0.2)
        
        # Boost for appropriate experience level
        experience_boost = 0.1 if requirements['experience_level'] in ['entry', 'mid'] else 0.05
        
        # Boost for company culture fit
        culture_boost = len(requirements.get('culture_keywords', [])) * 0.01
        
        priority_score = base_score + skill_boost + experience_boost + culture_boost
        return min(round(priority_score, 3), 1.0)
    
    def generate_recommendations(self, requirements: Dict, similarity_score: float) -> List[str]:
        """Generate actionable recommendations for improving application success."""
        recommendations = []
        
        if similarity_score < 0.3:
            recommendations.append("Consider focusing on positions that better match your current skill set")
        elif similarity_score < 0.6:
            recommendations.append("Good potential match - emphasize transferable skills in your application")
        else:
            recommendations.append("Excellent match - strong candidate for this position")
        
        # Skill-specific recommendations
        if len(requirements['skills']) > 10:
            recommendations.append("This role requires diverse technical skills - highlight your adaptability")
        
        # Experience level recommendations
        exp_level = requirements['experience_level']
        if exp_level == 'senior' and similarity_score > 0.7:
            recommendations.append("Consider emphasizing leadership and mentoring experience")
        elif exp_level == 'entry':
            recommendations.append("Focus on education, projects, and eagerness to learn")
        
        return recommendations
