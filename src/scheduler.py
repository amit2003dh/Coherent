"""
Pipeline Scheduler - Orchestrates the complete data pipeline

This module coordinates scraping, cleaning, enrichment, and database storage.
It serves as the main entry point for the job market intelligence system.
"""
import logging
import os
from datetime import datetime
import pandas as pd
from src.scraper.fetcher import JobFetcher
from src.scraper.parser import JobParser
from src.cleaning.transform import DataTransformer
from src.database.loader import DataLoader
from src.ai.enrich import JobEnricher
from src.utils.field_extractor import extract_fields
from src.utils.field_extractor import FIELD_SETS
import json

# 📋 Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline(enrich_with_ai: bool = False):
    """Execute the complete job market intelligence pipeline"""
    logger.info("=" * 50)
    logger.info("STARTING JOB MARKET INTELLIGENCE PIPELINE")
    logger.info("=" * 50)
    
    # Ensure data directories exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Step 1: Scrape job data from Indeed
    logger.info("STEP 1: Scraping job data from Indeed.com")
    fetcher = JobFetcher()
    parser = JobParser()
    
    # Fetch pages (returns empty list for demonstration)
    pages = fetcher.fetch_all_pages()
    
    # Parse pages to extract job information
    all_jobs = []
    for page_content in pages:
        jobs = parser.parse_page(page_content)
        all_jobs.extend(jobs)
    
    # If no real data was scraped, generate sample data
    if not all_jobs:
        logger.info("No data from scraping, generating sample data")
        all_jobs = parser._generate_sample_jobs(60)
    
    # Step 2: Clean and standardize job data
    logger.info("STEP 2: Cleaning and standardizing job data")
    transformer = DataTransformer()
    # Convert to DataFrame for cleaning
    df = pd.DataFrame(all_jobs)
    cleaned_df = transformer.clean_dataframe(df)
    cleaned_jobs = cleaned_df.to_dict('records')
    
    # Save cleaned data in multiple formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleaned_file = f"data/processed/jobs_cleaned_{timestamp}.json"
    with open(cleaned_file, 'w') as f:
        json.dump(cleaned_jobs, f, indent=2)
    logger.info(f"Cleaned data saved to {cleaned_file}")
    
    # Also save as CSV for compatibility
    csv_file = f"data/processed/jobs_cleaned_{timestamp}.csv"
    if cleaned_jobs:
        df = pd.DataFrame(cleaned_jobs)
        df.to_csv(csv_file, index=False)
        logger.info(f"Cleaned data saved to {csv_file}")
    
    # Step 3: AI enrichment (optional)
    if enrich_with_ai:
        logger.info("STEP 3: AI-powered skill enrichment")
        enricher = JobEnricher()
        enriched_jobs = enricher.enrich_jobs(cleaned_jobs)
        
        # Save enriched data
        enriched_file = f"data/processed/jobs_enriched_{timestamp}.json"
        with open(enriched_file, 'w') as f:
            json.dump(enriched_jobs, f, indent=2)
        logger.info(f"Enriched data saved to {enriched_file}")
    else:
        enriched_jobs = cleaned_jobs
    
    # Step 4: Extract specific fields
    logger.info("STEP 4: Extracting specific fields")
    from src.config import settings
    field_set = settings.extraction_fields
    logger.info(f"Using field set: {field_set}")
    
    # Extract only the specified fields
    field_extracted_jobs = extract_fields(enriched_jobs, field_set)
    logger.info(f"Extracted {len(field_extracted_jobs)} jobs with {len(FIELD_SETS[field_set])} fields each")
    
    # Step 5: Load data into database
    logger.info("STEP 5: Loading data into database")
    loader = DataLoader()
    inserted, updated = loader.load_jobs(field_extracted_jobs)
    
    # Step 5: Generate summary
    stats = loader.get_statistics()
    
    # Return comprehensive summary
    result = {
        'total_jobs': stats.get('total_jobs', 0),
        'companies': stats.get('company_count', 0),
        'locations': stats.get('location_count', 0),
        'avg_salary_min': stats.get('avg_salary_min', 0),
        'avg_salary_max': stats.get('avg_salary_max', 0)
    }
    logger.info("=" * 50)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total jobs in database: {stats.get('total_jobs', 0)}")
    logger.info(f"Companies: {stats.get('company_count', 0)}")
    logger.info(f"Locations: {stats.get('location_count', 0)}")
    
    if stats.get('avg_salary_min'):
        logger.info(f"Average salary range: ₹{stats.get('avg_salary_min', 0):,.0f} - ₹{stats.get('avg_salary_max', 0):,.0f}")
    
    logger.info("=" * 50)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 50)
    
    return {
        "jobs_collected": len(all_jobs),
        "jobs_cleaned": len(cleaned_jobs),
        "jobs_inserted": inserted,
        "jobs_updated": updated,
        "total_in_database": stats.get('total_jobs', 0)
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run job market intelligence pipeline")
    parser.add_argument("--enrich", action="store_true", help="Enable AI/ML enrichment")
    
    args = parser.parse_args()
    
    run_pipeline(enrich_with_ai=args.enrich)
