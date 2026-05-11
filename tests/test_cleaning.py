"""
Tests for the data cleaning module.
"""
import pytest
import pandas as pd
from src.cleaning.transform import DataTransformer


class TestDataTransformer:
    """Test cases for DataTransformer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = DataTransformer()
        
        # Sample test data
        self.sample_data = pd.DataFrame([
            {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'Bangalore',
                'salary_min': 1000000,
                'salary_max': 2000000,
                'skills': ['python', 'django'],
                'description': 'Looking for Python developer'
            },
            {
                'title': 'software engineer',  # Duplicate with different case
                'company': 'tech corp',
                'location': 'Bangalore',
                'salary_min': 1200000,
                'salary_max': 2200000,
                'skills': ['java', 'spring'],
                'description': 'Java developer position'
            },
            {
                'title': '',  # Missing title
                'company': 'Startup Inc',
                'location': 'Mumbai',
                'salary_min': None,
                'salary_max': None,
                'skills': [],
                'description': 'Frontend developer'
            }
        ])
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        result = self.transformer._remove_duplicates(self.sample_data)
        # Should remove the duplicate (first two records are duplicates after standardization)
        assert len(result) == 2
    
    def test_handle_missing_values(self):
        """Test handling missing values."""
        result = self.transformer._handle_missing_values(self.sample_data)
        
        # Check missing title is filled
        assert result.iloc[2]['title'] == 'Unknown'
        
        # Check missing salary is handled (should remain None)
        assert pd.isna(result.iloc[2]['salary_min'])
    
    def test_standardize_text(self):
        """Test text standardization."""
        result = self.transformer._standardize_text(self.sample_data)
        
        # Check text is lowercase and stripped
        assert result.iloc[0]['title'] == 'software engineer'
        assert result.iloc[0]['company'] == 'tech corp'
    
    def test_clean_salaries(self):
        """Test salary cleaning."""
        # Create data with invalid salaries
        test_data = pd.DataFrame([
            {'salary_min': 1000000, 'salary_max': 500000},  # min > max
            {'salary_min': -1000, 'salary_max': 2000000},  # negative salary
            {'salary_min': 1000000, 'salary_max': 2000000},  # valid
        ])
        
        result = self.transformer._clean_salaries(test_data)
        
        # Check min > max is swapped
        assert result.iloc[0]['salary_min'] == 500000
        assert result.iloc[0]['salary_max'] == 1000000
        
        # Check negative salary is set to None
        assert pd.isna(result.iloc[1]['salary_min'])
    
    def test_extract_skills(self):
        """Test skill extraction from descriptions."""
        test_data = pd.DataFrame([
            {'description': 'Looking for Python and Django developer', 'skills': []},
            {'description': 'Java Spring position with SQL knowledge', 'skills': ['java']},
            {'description': None, 'skills': []},
        ])
        
        result = self.transformer._extract_skills(test_data)
        
        # Check skills extracted from description
        assert 'python' in result.iloc[0]['skills']
        assert 'django' in result.iloc[0]['skills']
        
        # Check existing skills preserved
        assert 'java' in result.iloc[1]['skills']
    
    def test_validate_data(self):
        """Test data validation."""
        result = self.transformer._validate_data(self.sample_data)
        
        # Should remove record with 'unknown' title
        assert len(result) < len(self.sample_data)
        assert all(result['title'] != 'unknown')
    
    def test_clean_dataframe_integration(self):
        """Test the complete cleaning pipeline."""
        result = self.transformer.clean_dataframe(self.sample_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(self.sample_data)
        assert all(result['title'] != '')  # No empty titles
    
    def test_transform_to_records(self):
        """Test transformation to records."""
        cleaned_df = self.transformer.clean_dataframe(self.sample_data)
        records = self.transformer.transform_to_records(cleaned_df)
        
        assert isinstance(records, list)
        assert len(records) == len(cleaned_df)
        assert isinstance(records[0], dict)


if __name__ == "__main__":
    pytest.main([__file__])
