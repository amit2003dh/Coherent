"""
Database models and schema definition.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from src.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Job(Base):
    """Job posting model."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True, default='INR')
    posted_date = Column(DateTime, nullable=True)
    skills = Column(Text, nullable=True)  # JSON string
    url = Column(String(500), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}')>"


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def upsert_jobs(self, jobs: list) -> tuple[int, int]:
        """Insert or update job records."""
        from datetime import datetime
        import json
        session = self.get_session()
        inserted = 0
        updated = 0
        
        try:
            for job_data in jobs:
                # Convert string dates to datetime objects
                job_data_copy = job_data.copy()
                
                if 'posted_date' in job_data_copy and isinstance(job_data_copy['posted_date'], str):
                    try:
                        job_data_copy['posted_date'] = datetime.strptime(job_data_copy['posted_date'], '%Y-%m-%d')
                    except (ValueError, TypeError):
                        job_data_copy['posted_date'] = None
                
                if 'scraped_at' in job_data_copy and isinstance(job_data_copy['scraped_at'], str):
                    try:
                        job_data_copy['scraped_at'] = datetime.strptime(job_data_copy['scraped_at'], '%Y-%m-%dT%H:%M:%S')
                    except (ValueError, TypeError):
                        job_data_copy['scraped_at'] = datetime.utcnow()
                
                # Convert skills list to JSON string
                if 'skills' in job_data_copy and isinstance(job_data_copy['skills'], list):
                    job_data_copy['skills'] = json.dumps(job_data_copy['skills'])
                
                # Check if job already exists by URL
                existing_job = session.query(Job).filter(Job.url == job_data_copy.get('url')).first()
                
                if existing_job:
                    # Update existing record
                    for key, value in job_data_copy.items():
                        if hasattr(existing_job, key) and key != 'id':
                            setattr(existing_job, key, value)
                    existing_job.scraped_at = datetime.utcnow()
                    updated += 1
                else:
                    # Insert new record
                    job = Job(**job_data_copy)
                    session.add(job)
                    inserted += 1
            
            session.commit()
            logger.info(f"Upsert complete: {inserted} inserted, {updated} updated")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error upserting jobs: {e}")
            raise
        finally:
            session.close()
        
        return inserted, updated
    
    def get_jobs(self, limit: int = 100, offset: int = 0, filters: dict = None) -> list:
        """Get jobs with optional filters."""
        session = self.get_session()
        
        try:
            query = session.query(Job)
            
            # Apply filters
            if filters:
                if filters.get('company'):
                    query = query.filter(Job.company.ilike(f"%{filters['company']}%"))
                if filters.get('location'):
                    query = query.filter(Job.location.ilike(f"%{filters['location']}%"))
                if filters.get('min_salary'):
                    query = query.filter(Job.salary_min >= filters['min_salary'])
                if filters.get('max_salary'):
                    query = query.filter(Job.salary_max <= filters['max_salary'])
                if filters.get('skill'):
                    query = query.filter(Job.skills.ilike(f"%{filters['skill']}%"))
            
            # Order by most recent scraped_at and apply pagination
            jobs = query.order_by(Job.scraped_at.desc()).offset(offset).limit(limit).all()
            
            # Convert to dictionaries
            result = []
            for job in jobs:
                job_dict = {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'salary_currency': job.salary_currency,
                    'posted_date': job.posted_date.isoformat() if job.posted_date else None,
                    'skills': job.skills,
                    'url': job.url,
                    'description': job.description,
                    'scraped_at': job.scraped_at.isoformat() if job.scraped_at else None
                }
                result.append(job_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            return []
        finally:
            session.close()
    
    def get_job_stats(self) -> dict:
        """Get job statistics."""
        session = self.get_session()
        
        try:
            total_jobs = session.query(Job).count()
            
            # Salary statistics
            salary_min_avg = session.query(func.avg(Job.salary_min)).filter(Job.salary_min.isnot(None)).scalar()
            salary_max_avg = session.query(func.avg(Job.salary_max)).filter(Job.salary_max.isnot(None)).scalar()
            
            # Company count
            company_count = session.query(Job.company).distinct().count()
            
            # Location count
            location_count = session.query(Job.location).distinct().count()
            
            return {
                'total_jobs': total_jobs,
                'company_count': company_count,
                'location_count': location_count,
                'avg_salary_min': salary_min_avg if salary_min_avg else 0,
                'avg_salary_max': salary_max_avg if salary_max_avg else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting job stats: {e}")
            return {}
        finally:
            session.close()
