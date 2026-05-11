from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/jobs.db"
    
    # Scraper
    scraper_delay_seconds: int = 3
    max_retries: int = 3
    request_timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # Data Source Configuration
    base_url: str = "https://linkedin.com/jobs"
    max_pages: int = 3
    search_query: str = "software engineer"
    location: str = "India"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
