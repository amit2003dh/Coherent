"""
Data loader for database operations.
"""
import logging
from typing import List, Dict, Optional
from src.database.models import DatabaseManager, Job

logger = logging.getLogger(__name__)


class DataLoader:
    """Data loader for job data."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def load_jobs(self, jobs: List[Dict]) -> tuple[int, int]:
        """Load jobs into database.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Tuple of (inserted_count, updated_count)
        """
        # Remove fields not in database schema
        cleaned_jobs = []
        for job in jobs:
            job_copy = job.copy()
            # Remove fields that don't exist in database schema
            fields_to_remove = ['job_level', 'experience_years', 'urgency']
            for field in fields_to_remove:
                if field in job_copy:
                    del job_copy[field]
            cleaned_jobs.append(job_copy)
        
        return self.db_manager.upsert_jobs(cleaned_jobs)
    
    def get_jobs(self, limit: int = 100, offset: int = 0, filters: dict = None) -> List[Dict]:
        """Retrieve jobs from database with filters."""
        return self.db_manager.get_jobs(limit=limit, offset=offset, filters=filters)
    
    def get_job_stats(self) -> dict:
        """Get job statistics."""
        return self.db_manager.get_job_stats()
    
    def get_statistics(self) -> dict:
        """Get job statistics (alias for get_job_stats)."""
        return self.db_manager.get_job_stats()
    
    def get_salary_analytics(self) -> dict:
        """Get salary analytics."""
        session = self.db_manager.get_session()
        
        try:
            # Get salary statistics
            from sqlalchemy import func
            salary_stats = session.query(
                func.avg(Job.salary_min).label('avg_salary_min'),
                func.avg(Job.salary_max).label('avg_salary_max'),
                func.max(Job.salary_max).label('max_salary_max'),
                func.min(Job.salary_min).label('min_salary_min')
            ).filter(Job.salary_min.isnot(None)).first()
            
            return {
                'avg_salary_min': float(salary_stats.avg_salary_min) if salary_stats.avg_salary_min else 0,
                'avg_salary_max': float(salary_stats.avg_salary_max) if salary_stats.avg_salary_max else 0,
                'max_salary_max': float(salary_stats.max_salary_max) if salary_stats.max_salary_max else 0,
                'min_salary_min': float(salary_stats.min_salary_min) if salary_stats.min_salary_min else 0
            }
        except Exception as e:
            logger.error(f"Error getting salary analytics: {e}")
            return {}
        finally:
            session.close()
    
    def get_top_skills(self, limit: int = 20) -> List[Dict]:
        """Get top skills by frequency."""
        session = self.db_manager.get_session()
        
        try:
            # Get all jobs with skills
            jobs = session.query(Job).filter(Job.skills.isnot(None)).all()
            
            # Parse and count skills
            from collections import Counter
            skill_counter = Counter()
            
            for job in jobs:
                if job.skills:
                    # Handle different skill formats
                    if isinstance(job.skills, str):
                        # Remove braces and quotes, split by comma
                        cleaned = job.skills.replace('{', '').replace('}', '').replace('"', '').replace('[', '').replace(']', '')
                        skills_list = [s.strip() for s in cleaned.split(',') if s.strip()]
                        skill_counter.update(skills_list)
                    elif isinstance(job.skills, list):
                        skill_counter.update(job.skills)
            
            # Get top skills
            top_skills = skill_counter.most_common(limit)
            return [{"skill": skill, "count": count} for skill, count in top_skills]
        except Exception as e:
            logger.error(f"Error getting top skills: {e}")
            return []
        finally:
            session.close()
