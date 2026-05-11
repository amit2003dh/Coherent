"""
 Job Market Intelligence Pipeline - Main Runner

This script executes the complete data pipeline from scraping to dashboard.
It serves as a compatibility wrapper for the new modular architecture.
"""
import logging
import argparse
from src.scheduler import run_pipeline

 Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """ Main pipeline execution function"""
    parser = argparse.ArgumentParser(
        description=" Run Job Market Intelligence Pipeline",
        epilog="Example: python run_pipeline.py --max-pages 5 --enrich"
    )
    
    # Pipeline configuration options
    parser.add_argument(
        "--max-pages", 
        type=int, 
        default=10,
        help="Maximum number of pages to scrape (default: 10)"
    )
    parser.add_argument(
        "--skip-scrape", 
        action="store_true", 
        help="Skip scraping step and use existing raw data"
    )
    parser.add_argument(
        "--enrich", 
        action="store_true", 
        help="Enable AI/ML enrichment for skill analysis"
    )
    
    args = parser.parse_args()
    
    # Execute the complete pipeline
    logger.info("Starting Job Market Intelligence Pipeline...")
    logger.info(f"Configuration: max_pages={args.max_pages}, skip_scrape={args.skip_scrape}, enrich={args.enrich}")
    
    try:
        result = run_pipeline(enrich_with_ai=args.enrich)
        
        # Log successful completion
        logger.info("Pipeline completed successfully!")
        logger.info(f"Results: {result}")
        
        return result
        
    except Exception as e:
        # Handle pipeline errors gracefully
        logger.error(f"Pipeline failed: {str(e)}")
        logger.error("Check logs and configuration for troubleshooting")
        raise

if __name__ == "__main__":
    main()
