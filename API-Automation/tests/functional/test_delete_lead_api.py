"""
Test Cases for Delete Lead API (DELETE /api/v1/leads/{lead_id})
"""
import pytest
from src.utils.assertions import APIAssertions as Assert


@pytest.mark.delete
@pytest.mark.smoke
@pytest.mark.positive
class TestDeleteLeadAPI:
    """Positive test cases for Delete Lead API"""
    
    def test_delete_lead_success(self, api_client, sample_lead_data):
        """TC-028: Delete existing lead"""
        # Create lead to delete
        lead = api_client.create_lead(sample_lead_data)
        
        # Delete the lead
        result = api_client.delete_lead(lead.id)
        assert result is True
        
        # Verify lead is deleted
        response = api_client.get_lead_raw(lead.id)
        Assert.assert_status_code(response, 404)
    
    def test_delete_lead_response_code(self, api_client, sample_lead_data):
        """TC-029: Verify delete lead returns 204"""
        lead = api_client.create_lead(sample_lead_data)
        
        response = api_client.delete_lead_raw(lead.id)
        Assert.assert_status_code(response, 204)


@pytest.mark.delete
@pytest.mark.negative
class TestDeleteLeadAPINegative:
    """Negative test cases for Delete Lead API"""
    
    def test_delete_nonexistent_lead(self, api_client):
        """TC-030: Delete non-existent lead"""
        response = api_client.delete_lead_raw("99999999-9999-9999-9999-999999999999")
        Assert.assert_status_code(response, 404)
    
    def test_delete_already_deleted_lead(self, api_client, sample_lead_data):
        """TC-031: Delete already deleted lead"""
        # Create and delete lead
        lead = api_client.create_lead(sample_lead_data)
        api_client.delete_lead(lead.id)
        
        # Try to delete again
        response = api_client.delete_lead_raw(lead.id)
        Assert.assert_status_code(response, 404)
    
    def test_delete_lead_invalid_id(self, api_client):
        """TC-032: Delete lead with invalid ID"""
        response = api_client.delete_lead_raw("invalid-id")
        Assert.assert_status_code(response, 404)
