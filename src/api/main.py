"""
FastAPI application for job market intelligence API.
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import logging
from src.database.loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Job Market Intelligence API",
    description="API for accessing job market data and analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data loader
data_loader = DataLoader()


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Job Market Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "jobs": "/jobs",
            "stats": "/stats",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "job-market-api"}


@app.get("/jobs")
def get_jobs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None),
    max_salary: Optional[float] = Query(None),
    skill: Optional[str] = Query(None)
):
    """Get job listings with optional filters."""
    try:
        filters = {}
        if company:
            filters['company'] = company
        if location:
            filters['location'] = location
        if min_salary:
            filters['min_salary'] = min_salary
        if max_salary:
            filters['max_salary'] = max_salary
        if skill:
            filters['skill'] = skill
        
        jobs = data_loader.get_jobs(limit=limit, offset=offset, filters=filters)
        
        return {
            "jobs": jobs,
            "count": len(jobs),
            "limit": limit,
            "offset": offset,
            "filters": filters
        }
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    """Get a specific job by ID."""
    # This would require adding a get_job_by_id method to the database
    raise HTTPException(status_code=501, detail="Not implemented")


@app.get("/stats")
def get_stats():
    """Get job market statistics."""
    try:
        stats = data_loader.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/analytics/salary")
def get_salary_analytics():
    """Get salary analytics."""
    try:
        jobs = data_loader.get_jobs(limit=1000)
        
        if not jobs:
            return {"message": "No data available"}
        
        # Calculate salary statistics
        salaries_min = [j['salary_min'] for j in jobs if j['salary_min']]
        salaries_max = [j['salary_max'] for j in jobs if j['salary_max']]
        
        return {
            "avg_salary_min": sum(salaries_min) / len(salaries_min) if salaries_min else 0,
            "avg_salary_max": sum(salaries_max) / len(salaries_max) if salaries_max else 0,
            "max_salary": max(salaries_max) if salaries_max else 0,
            "min_salary": min(salaries_min) if salaries_min else 0,
            "jobs_with_salary": len([j for j in jobs if j['salary_min'] or j['salary_max']]),
            "total_jobs": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Error calculating salary analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/analytics/skills")
def get_skill_analytics():
    """Get skill demand analytics."""
    try:
        jobs = data_loader.get_jobs(limit=1000)
        
        if not jobs:
            return {"message": "No data available"}
        
        # Count skills
        skill_counts = {}
        for job in jobs:
            if job['skills']:
                # Parse skills string (assuming JSON or comma-separated)
                skills = job['skills']
                if isinstance(skills, str):
                    import json
                    try:
                        skills = json.loads(skills)
                    except:
                        skills = [s.strip() for s in skills.split(',')]
                
                for skill in skills:
                    if skill:
                        skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by count
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "top_skills": [{"skill": skill, "count": count} for skill, count in sorted_skills[:20]],
            "total_unique_skills": len(skill_counts)
        }
        
    except Exception as e:
        logger.error(f"Error calculating skill analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
