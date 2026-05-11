"""
HTML/JSON parsing logic for job data extraction.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

logger = logging.getLogger(__name__)


class JobParser:
    """Parses job data from HTML/JSON responses."""
    
    def __init__(self):
        pass
    
    def parse_page(self, content: str) -> List[Dict]:
        """Parse a single page of job listings."""
        # For demonstration, generate sample data when no content is provided
        if not content:
            return self._generate_sample_jobs()
        
        # In production, parse actual HTML/JSON here
        return []
    
    def _generate_sample_jobs(self, count: int = 20) -> List[Dict]:
        """Generate realistic sample job data."""
        companies = [
            "Microsoft", "Google", "Amazon", "Meta", "Apple", "IBM", "Oracle", "SAP",
            "TCS", "Infosys", "Wipro", "HCL", "Tech Mahindra", "L&T Infotech",
            "Accenture", "Capgemini", "Deloitte", "KPMG", "EY", "PwC",
            "Flipkart", "Swiggy", "Zomato", "Ola", "Paytm", "PhonePe", "CRED"
        ]
        
        locations = [
            "Bangalore, Karnataka", "Hyderabad, Telangana", "Mumbai, Maharashtra",
            "Delhi NCR", "Chennai, Tamil Nadu", "Pune, Maharashtra",
            "Gurgaon, Haryana", "Noida, Uttar Pradesh", "Kolkata, West Bengal"
        ]
        
        titles = [
            "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
            "Backend Engineer", "Frontend Engineer", "DevOps Engineer",
            "Data Engineer", "Machine Learning Engineer", "Cloud Architect"
        ]
        
        skills_pools = [
            ["python", "django", "postgresql", "docker", "kubernetes"],
            ["java", "spring boot", "microservices", "aws", "kafka"],
            ["javascript", "react", "node.js", "mongodb", "graphql"],
            ["python", "tensorflow", "pytorch", "nlp", "machine learning"],
            ["go", "kubernetes", "docker", "prometheus", "grafana"]
        ]
        
        jobs = []
        base_date = datetime.now()
        
        for i in range(count):
            title = random.choice(titles)
            company = random.choice(companies)
            location = random.choice(locations)
            skills = random.choice(skills_pools)
            
            # Generate salary based on title
            if "Senior" in title:
                salary_min = random.randint(1500000, 2500000)
                salary_max = random.randint(2500001, 4000000)
            elif "Engineer" in title:
                salary_min = random.randint(800000, 1500000)
                salary_max = random.randint(1500001, 2500000)
            else:
                salary_min = random.randint(600000, 1200000)
                salary_max = random.randint(1200001, 2000000)
            
            # Random posted date within last 30 days
            posted_date = base_date - timedelta(days=random.randint(0, 30))
            
            job = {
                'title': title,
                'company': company,
                'location': location,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_currency': 'INR',
                'posted_date': posted_date.isoformat(),
                'skills': skills,
                'url': f"https://example.com/jobs/{random.randint(10000000, 99999999)}",
                'description': f"We are looking for a {title} to join our team at {company}.",
                'scraped_at': datetime.now().isoformat()
            }
            
            jobs.append(job)
        
        return jobs
    
    def extract_field(self, element, selector: str, attr: str = None) -> Optional[str]:
        """Safely extract a field from an HTML element."""
        try:
            if attr:
                return element.get(attr)
            return element.get_text(strip=True)
        except Exception as e:
            logger.warning(f"Failed to extract field with selector '{selector}': {e}")
            return None
