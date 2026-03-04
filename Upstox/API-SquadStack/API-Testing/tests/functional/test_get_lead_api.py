"""
Test Cases for Get Lead API (GET /api/v1/leads/{lead_id})
"""
import pytest
from src.utils.assertions import APIAssertions as Assert
from src.utils.logger import logger


@pytest.mark.read
@pytest.mark.smoke
@pytest.mark.positive
class TestGetLeadAPI:
    """Positive test cases for Get Lead API"""
    
    def test_get_lead_by_valid_id(self, api_client, created_lead):
        """TC-015: Get lead by valid ID"""
        logger.info(f"Testing get lead with ID: {created_lead.id}")
        
        response = api_client.get_lead(created_lead.id)
        
        assert response.id == created_lead.id
        assert response.email == created_lead.email
        assert response.first_name == created_lead.first_name
    
    def test_get_lead_response_schema(self, api_client, created_lead):
        """TC-016: Verify get lead response schema"""
        response = api_client.get_lead_raw(created_lead.id)
        
        Assert.assert_status_code(response, 200)
        Assert.assert_json_schema(response, {
            "type": "object",
            "required": ["id", "firstName", "lastName", "email"]
        })
    
    def test_get_lead_response_time(self, api_client, created_lead):
        """TC-017: Verify get lead response time"""
        response = api_client.get_lead_raw(created_lead.id)
        Assert.assert_response_time(response, 1000)  # 1 second


@pytest.mark.read
@pytest.mark.negative
class TestGetLeadAPINegative:
    """Negative test cases for Get Lead API"""
    
    def test_get_lead_with_invalid_id(self, api_client):
        """TC-018: Get lead with invalid ID format"""
        response = api_client.get_lead_raw("invalid-id-123")
        Assert.assert_status_code(response, 404)
    
    def test_get_lead_with_nonexistent_id(self, api_client):
        """TC-019: Get lead with non-existent ID"""
        response = api_client.get_lead_raw("99999999-9999-9999-9999-999999999999")
        Assert.assert_status_code(response, 404)
        Assert.assert_error_message(response, expected_message="not found")
    
    def test_get_lead_with_empty_id(self, api_client):
        """TC-020: Get lead with empty ID"""
        response = api_client.get_lead_raw("")
        Assert.assert_status_range(response, 400, 404)


@pytest.mark.read
@pytest.mark.security
class TestGetLeadAPISecurity:
    """Security tests for Get Lead API"""
    
    def test_get_lead_sql_injection_attempt(self, api_client):
        """TC-021: SQL injection attempt in lead ID"""
        malicious_id = "1' OR '1'='1"
        response = api_client.get_lead_raw(malicious_id)
        
        # Should not return data, should return 404
        Assert.assert_status_code(response, 404)
