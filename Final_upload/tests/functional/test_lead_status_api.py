"""
Test Cases for Lead Status API (GET /api/v1/leads/{lead_id}/status)
"""
import pytest
from src.models.lead_models import LeadStatus
from src.utils.assertions import APIAssertions as Assert


@pytest.mark.status
@pytest.mark.smoke
@pytest.mark.positive
class TestLeadStatusAPI:
    """Positive test cases for Lead Status API"""
    
    def test_get_lead_status(self, api_client, created_lead):
        """TC-044: Get status of existing lead"""
        response = api_client.get_lead_status(created_lead.id)
        
        assert response.lead_id == created_lead.id
        assert response.status == LeadStatus.NEW.value
    
    def test_get_lead_status_after_update(self, api_client, created_lead):
        """TC-045: Get status after lead update"""
        from src.models.lead_models import UpdateLeadRequest
        
        # Update status
        api_client.update_lead(
            created_lead.id,
            UpdateLeadRequest(status=LeadStatus.CONTACTED)
        )
        
        # Check status
        response = api_client.get_lead_status(created_lead.id)
        assert response.status == LeadStatus.CONTACTED.value
        assert response.previous_status == LeadStatus.NEW.value


@pytest.mark.status
@pytest.mark.negative
class TestLeadStatusAPINegative:
    """Negative test cases for Lead Status API"""
    
    def test_get_status_nonexistent_lead(self, api_client):
        """TC-046: Get status of non-existent lead"""
        response = api_client.get_lead_status_raw("99999999-9999-9999-9999-999999999999")
        Assert.assert_status_code(response, 404)
    
    def test_get_status_invalid_id(self, api_client):
        """TC-047: Get status with invalid ID"""
        response = api_client.get_lead_status_raw("invalid")
        Assert.assert_status_code(response, 404)
