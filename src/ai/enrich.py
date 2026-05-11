"""
AI/ML enrichment layer for job data.
"""
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class JobEnricher:
    """Enriches job data with AI/ML insights."""
    
    def __init__(self):
        pass
    
    def classify_job_level(self, job: Dict) -> str:
        """Classify job level based on title and requirements."""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        salary_min = job.get('salary_min', 0)
        salary_max = job.get('salary_max', 0)
        avg_salary = (salary_min + salary_max) / 2 if salary_min and salary_max else 0
        
        # Check for level indicators in title
        if any(keyword in title for keyword in ['senior', 'lead', 'principal', 'sr.', 'sr ']):
            return 'senior'
        elif any(keyword in title for keyword in ['junior', 'jr.', 'jr ', 'entry', 'associate']):
            return 'junior'
        elif any(keyword in title for keyword in ['manager', 'head', 'director', 'vp']):
            return 'management'
        
        # Check salary ranges for level inference
        if avg_salary > 2000000:  # Above 20L INR
            return 'senior'
        elif avg_salary < 800000:  # Below 8L INR
            return 'junior'
        
        return 'mid'
    
    def extract_experience_years(self, job: Dict) -> Optional[int]:
        """Extract years of experience from job description."""
        description = job.get('description', '').lower()
        
        # Look for patterns like "5+ years", "3-5 years", etc.
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                if len(match.groups()) == 2:
                    # Range like "3-5 years"
                    return int(match.group(1))
                else:
                    # Single number like "5+ years"
                    return int(match.group(1))
        
        return None
    
    def assess_urgency(self, job: Dict) -> str:
        """Assess hiring urgency based on job posting."""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        
        urgent_keywords = [
            'urgent', 'immediate', 'asap', 'immediately', 
            'priority', 'critical', 'hiring immediately'
        ]
        
        if any(keyword in title for keyword in urgent_keywords):
            return 'high'
        elif any(keyword in description for keyword in urgent_keywords):
            return 'medium'
        
        return 'low'
    
    def generate_job_summary(self, job: Dict) -> str:
        """Generate a concise summary of the job."""
        title = job.get('title', 'Unknown')
        company = job.get('company', 'Unknown')
        location = job.get('location', 'Unknown')
        salary_min = job.get('salary_min')
        salary_max = job.get('salary_max')
        
        summary = f"{title} at {company} in {location}"
        
        if salary_min and salary_max:
            summary += f" (₹{salary_min:,.0f} - ₹{salary_max:,.0f})"
        elif salary_min:
            summary += f" (₹{salary_min:,.0f}+)"
        
        # Add key skills
        skills = job.get('skills', [])
        if skills and isinstance(skills, list) and len(skills) > 0:
            top_skills = skills[:3]
            summary += f". Key skills: {', '.join(top_skills)}"
        
        return summary
    
    def enrich_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Enrich a list of jobs with AI/ML insights."""
        enriched_jobs = []
        
        for job in jobs:
            enriched_job = job.copy()
            
            # Add enrichments
            enriched_job['job_level'] = self.classify_job_level(job)
            enriched_job['experience_years'] = self.extract_experience_years(job)
            enriched_job['urgency'] = self.assess_urgency(job)
            enriched_job['summary'] = self.generate_job_summary(job)
            
            enriched_jobs.append(enriched_job)
        
        logger.info(f"Enriched {len(jobs)} jobs with AI/ML insights")
        return enriched_jobs
    
    def generate_market_insights(self, jobs: List[Dict]) -> Dict:
        """Generate market insights from job data."""
        if not jobs:
            return {"message": "No data available"}
        
        # Analyze job levels
        levels = [job.get('job_level', 'unknown') for job in jobs]
        level_distribution = {}
        for level in levels:
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # Analyze urgency
        urgency_levels = [job.get('urgency', 'low') for job in jobs]
        urgency_distribution = {}
        for urgency in urgency_levels:
            urgency_distribution[urgency] = urgency_distribution.get(urgency, 0) + 1
        
        # Average experience required
        experience_years = [job.get('experience_years') for job in jobs if job.get('experience_years')]
        avg_experience = sum(experience_years) / len(experience_years) if experience_years else 0
        
        return {
            "total_jobs_analyzed": len(jobs),
            "job_level_distribution": level_distribution,
            "urgency_distribution": urgency_distribution,
            "average_experience_required": round(avg_experience, 1),
            "insights": {
                "most_common_level": max(level_distribution, key=level_distribution.get) if level_distribution else None,
                "hiring_urgency": "high" if urgency_distribution.get('high', 0) > len(jobs) * 0.3 else "normal",
                "experience_trend": "senior" if avg_experience > 5 else "entry-level" if avg_experience < 2 else "mid-level"
            }
        }


if __name__ == "__main__":
    # Test the enricher
    test_job = {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "location": "Bangalore",
        "salary_min": 1500000,
        "salary_max": 2500000,
        "description": "Looking for a senior engineer with 5+ years of experience in Python and cloud technologies. Urgent hiring."
    }
    
    enricher = JobEnricher()
    enriched = enricher.enrich_jobs([test_job])
    print("Enriched job:", enriched[0])
