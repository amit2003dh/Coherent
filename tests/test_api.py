"""
Tests for the API module.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestAPI:
    """Test cases for the API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_get_jobs(self):
        """Test getting jobs endpoint."""
        response = self.client.get("/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "count" in data
        assert "limit" in data
        assert isinstance(data["jobs"], list)
    
    def test_get_jobs_with_filters(self):
        """Test getting jobs with filters."""
        response = self.client.get("/jobs?company=tech&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert "filters" in data
    
    def test_get_stats(self):
        """Test stats endpoint."""
        response = self.client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        # Stats might be empty if no data, but should return valid structure
        assert isinstance(data, dict)
    
    def test_get_salary_analytics(self):
        """Test salary analytics endpoint."""
        response = self.client.get("/analytics/salary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain salary analytics or message about no data
    
    def test_get_skill_analytics(self):
        """Test skill analytics endpoint."""
        response = self.client.get("/analytics/skills")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain skill analytics or message about no data
    
    def test_get_jobs_invalid_limit(self):
        """Test getting jobs with invalid limit."""
        response = self.client.get("/jobs?limit=0")
        assert response.status_code == 422  # Validation error
        
        response = self.client.get("/jobs?limit=1000")
        assert response.status_code == 422  # Exceeds max limit
    
    def test_get_jobs_invalid_offset(self):
        """Test getting jobs with invalid offset."""
        response = self.client.get("/jobs?offset=-1")
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__])
