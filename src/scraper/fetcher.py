"""
HTTP fetching and pagination logic for job data scraper.
"""
import requests
import logging
from typing import List, Dict, Optional
from time import sleep
from src.config import settings

logger = logging.getLogger(__name__)


class JobFetcher:
    """Handles HTTP requests and pagination for job data."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': settings.base_url,
            'DNT': '1',
        })
    
    def fetch_page(self, page_num: int = 1) -> Optional[str]:
        """Fetch a single page of job listings."""
        try:
            # Note: This is a demonstration. In production, you would implement
            # actual pagination logic based on the target website's structure
            logger.info(f"Fetching page {page_num}")
            
            # Simulate network request
            sleep(settings.scraper_delay_seconds)
            
            # For demonstration, return None (will trigger sample data generation)
            return None
            
        except requests.RequestException as e:
            logger.error(f"Request failed for page {page_num}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching page {page_num}: {e}")
            return None
    
    def has_next_page(self, response: str) -> bool:
        """Check if there are more pages to fetch."""
        # In production, parse the response to determine if more pages exist
        return False
    
    def fetch_all_pages(self, max_pages: int = None) -> List[str]:
        """Fetch all pages up to the maximum limit."""
        max_pages = max_pages or settings.max_pages
        pages = []
        
        for page_num in range(1, max_pages + 1):
            page_content = self.fetch_page(page_num)
            if page_content is None:
                logger.info(f"No content for page {page_num}, stopping")
                break
            
            pages.append(page_content)
            
            if not self.has_next_page(page_content):
                logger.info("No more pages available")
                break
        
        logger.info(f"Fetched {len(pages)} pages")
        return pages
