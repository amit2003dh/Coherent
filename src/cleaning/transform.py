"""
Data cleaning and transformation logic using pandas.
"""
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforms and cleans raw job data."""
    
    def __init__(self):
        pass
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the job dataframe."""
        logger.info(f"Starting cleaning for {len(df)} records")
        
        # Remove duplicates
        original_count = len(df)
        df = self._remove_duplicates(df)
        duplicates_removed = original_count - len(df)
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Standardize text fields
        df = self._standardize_text(df)
        
        # Parse and standardize dates
        df = self._standardize_dates(df)
        
        # Clean salary data
        df = self._clean_salaries(df)
        
        # Extract skills from descriptions
        df = self._extract_skills(df)
        
        # Validate data
        df = self._validate_data(df)
        
        logger.info(f"Cleaning complete: {len(df)} records retained")
        logger.info(f"  - Duplicates removed: {duplicates_removed}")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate job postings."""
        # Use combination of title, company, and location for deduplication
        df = df.drop_duplicates(subset=['title', 'company', 'location'], keep='first')
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataframe."""
        # Fill missing critical fields
        df['title'] = df['title'].fillna('Unknown')
        df.loc[df['title'] == '', 'title'] = 'Unknown'
        df['company'] = df['company'].fillna('Unknown Company')
        df['location'] = df['location'].fillna('Unknown Location')
        
        # For optional fields, use None
        df['salary_min'] = df['salary_min'].where(pd.notna(df['salary_min']), None)
        df['salary_max'] = df['salary_max'].where(pd.notna(df['salary_max']), None)
        df['skills'] = df['skills'].fillna('[]')
        
        return df
    
    def _standardize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize text fields."""
        text_columns = ['title', 'company', 'location']
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date formats to ISO 8601 strings."""
        if 'posted_date' in df.columns:
            df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce')
            df['posted_date'] = df['posted_date'].dt.strftime('%Y-%m-%d')
        
        if 'scraped_at' in df.columns:
            df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')
            df['scraped_at'] = df['scraped_at'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        return df
    
    def _clean_salaries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate salary data."""
        # Ensure salary_min <= salary_max
        mask = (df['salary_min'] > df['salary_max']) & df['salary_min'].notna() & df['salary_max'].notna()
        df.loc[mask, ['salary_min', 'salary_max']] = df.loc[mask, ['salary_max', 'salary_min']].values
        
        # Remove negative salaries
        df['salary_min'] = df['salary_min'].where(df['salary_min'] >= 0, None)
        df['salary_max'] = df['salary_max'].where(df['salary_max'] >= 0, None)
        
        return df
    
    def _extract_skills(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and normalize skills from job descriptions."""
        if 'description' in df.columns:
            # Common tech skills
            skill_keywords = [
                'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
                'node.js', 'django', 'flask', 'sql', 'nosql', 'mongodb', 'postgresql',
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'linux',
                'machine learning', 'data science', 'analytics', 'excel', 'tableau'
            ]
            
            def extract_from_description(desc):
                if pd.isna(desc):
                    return []
                
                desc_lower = str(desc).lower()
                found_skills = []
                
                for skill in skill_keywords:
                    if skill in desc_lower:
                        found_skills.append(skill)
                
                return found_skills
            
            # Only extract if skills column is empty or contains empty lists
            mask = df['skills'].isna() | (df['skills'] == '[]')
            df.loc[mask, 'skills'] = df.loc[mask, 'description'].apply(extract_from_description)
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate data and remove invalid records."""
        # Remove records with missing critical fields
        df = df[df['title'].notna() & (df['title'] != 'unknown') & (df['title'] != '')]
        
        # Ensure salary ranges are reasonable (between 10k and 10M INR)
        df = df[
            ((df['salary_min'].isna()) | ((df['salary_min'] >= 10000) & (df['salary_min'] <= 10000000))) &
            ((df['salary_max'].isna()) | ((df['salary_max'] >= 10000) & (df['salary_max'] <= 10000000)))
        ]
        
        return df
    
    def transform_to_records(self, df: pd.DataFrame) -> List[Dict]:
        """Transform dataframe to list of dictionaries."""
        # Convert NaN to None for JSON serialization
        df = df.where(pd.notna(df), None)
        return df.to_dict('records')
