"""
Field extraction utility for job data.
"""

from typing import List, Dict, Set
from src.config import settings

# Define field sets for different extraction levels
FIELD_SETS = {
    "minimal": {"title", "company", "location", "url"},
    "essential": {"title", "company", "location", "salary_min", "salary_max", "url"},
    "core": {"title", "company", "location", "salary_min", "salary_max", "skills", "url"}
}

def extract_fields(jobs: List[Dict], field_set: str = None) -> List[Dict]:
    """
    Extract specific fields from job data based on field set.
    
    Args:
        jobs: List of job dictionaries
        field_set: Field set to use ("minimal", "essential", "core")
        
    Returns:
        List of job dictionaries with only specified fields
    """
    if field_set is None:
        field_set = settings.extraction_fields
    
    if field_set not in FIELD_SETS:
        raise ValueError(f"Invalid field set: {field_set}. Available: {list(FIELD_SETS.keys())}")
    
    fields_to_keep = FIELD_SETS[field_set]
    
    extracted_jobs = []
    for job in jobs:
        # Create new job dict with only specified fields
        extracted_job = {}
        for field in fields_to_keep:
            if field in job:
                extracted_job[field] = job[field]
        
        extracted_jobs.append(extracted_job)
    
    return extracted_jobs

def get_available_field_sets() -> Dict[str, Set[str]]:
    """Get all available field sets."""
    return FIELD_SETS.copy()
