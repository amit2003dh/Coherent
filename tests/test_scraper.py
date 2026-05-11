"""
Tests for the scraper module.
"""
import pytest
from unittest.mock import Mock, patch
from src.scraper.fetcher import JobFetcher
from src.scraper.parser import JobParser


class TestJobFetcher:
    """Test cases for JobFetcher."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = JobFetcher()
    
    @patch('src.scraper.fetcher.sleep')
    def test_fetch_page(self, mock_sleep):
        """Test fetching a page."""
        result = self.fetcher.fetch_page(1)
        # For demonstration, should return None (triggers sample data)
        assert result is None
        mock_sleep.assert_called_once()
    
    def test_has_next_page(self):
        """Test next page detection."""
        assert not self.fetcher.has_next_page("")  # Empty content has no next page
    
    def test_fetch_all_pages(self):
        """Test fetching all pages."""
        pages = self.fetcher.fetch_all_pages(max_pages=2)
        assert isinstance(pages, list)


class TestJobParser:
    """Test cases for JobParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JobParser()
    
    def test_parse_page_empty(self):
        """Test parsing empty page content."""
        jobs = self.parser.parse_page("")
        assert isinstance(jobs, list)
        # Should generate sample jobs
        assert len(jobs) > 0
    
    def test_parse_page_with_content(self):
        """Test parsing page with content."""
        jobs = self.parser.parse_page("<html><body>Test content</body></html>")
        assert isinstance(jobs, list)
        # For now, returns empty list for non-empty content
    
    def test_generate_sample_jobs(self):
        """Test sample job generation."""
        jobs = self.parser._generate_sample_jobs(5)
        assert len(jobs) == 5
        
        # Check job structure
        job = jobs[0]
        required_fields = ['title', 'company', 'location', 'salary_min', 'salary_max', 'skills']
        for field in required_fields:
            assert field in job
    
    def test_extract_field(self):
        """Test field extraction."""
        # Mock element with get_text method
        mock_element = Mock()
        mock_element.get_text.return_value = "Test Title"
        
        result = self.parser.extract_field(mock_element, "title")
        assert result == "Test Title"
        
        # Test with attribute
        mock_element.get.return_value = "test-url"
        result = self.parser.extract_field(mock_element, "link", attr="href")
        assert result == "test-url"


if __name__ == "__main__":
    pytest.main([__file__])
