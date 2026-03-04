"""
Test Cases for Update Lead API (PUT /api/v1/leads/{lead_id})
"""
import pytest
from src.models.lead_models import UpdateLeadRequest, LeadStatus
from src.utils.assertions import APIAssertions as Assert


@pytest.mark.update
@pytest.mark.smoke
@pytest.mark.positive
class TestUpdateLeadAPI:
    """Positive test cases for Update Lead API"""
    
    def test_update_lead_email(self, api_client, created_lead, unique_email):
        """TC-022: Update lead email"""
        update_data = UpdateLeadRequest(email=unique_email)
        
        response = api_client.update_lead(created_lead.id, update_data)
        
        assert response.email == unique_email
        assert response.id == created_lead.id
    
    def test_update_lead_status(self, api_client, created_lead):
        """TC-023: Update lead status"""
        update_data = UpdateLeadRequest(status=LeadStatus.CONTACTED)
        
        response = api_client.update_lead(created_lead.id, update_data)
        
        assert response.status == LeadStatus.CONTACTED.value
    
    def test_update_lead_multiple_fields(self, api_client, created_lead, unique_email):
        """TC-024: Update multiple lead fields"""
        update_data = UpdateLeadRequest(
            email=unique_email,
            first_name="Updated",
            last_name="Name",
            company="New Company",
            status=LeadStatus.QUALIFIED
        )
        
        response = api_client.update_lead(created_lead.id, update_data)
        
        assert response.email == unique_email
        assert response.first_name == "Updated"
        assert response.last_name == "Name"
        assert response.company == "New Company"
        assert response.status == LeadStatus.QUALIFIED.value


@pytest.mark.update
@pytest.mark.negative
class TestUpdateLeadAPINegative:
    """Negative test cases for Update Lead API"""
    
    def test_update_nonexistent_lead(self, api_client, unique_email):
        """TC-025: Update non-existent lead"""
        update_data = UpdateLeadRequest(email=unique_email)
        
        response = api_client.update_lead_raw(
            "99999999-9999-9999-9999-999999999999",
            update_data.model_dump(by_alias=True)
        )
        
        Assert.assert_status_code(response, 404)
    
    def test_update_lead_with_invalid_email(self, api_client, created_lead):
        """TC-026: Update lead with invalid email"""
        response = api_client.update_lead_raw(
            created_lead.id,
            {"email": "invalid-email"}
        )
        
        Assert.assert_status_range(response, 400, 422)
    
    def test_update_lead_with_duplicate_email(self, api_client, created_lead, sample_lead_data):
        """TC-027: Update lead with email already in use"""
        # Create another lead
        other_lead = api_client.create_lead(sample_lead_data)
        
        # Try to update first lead with second lead's email
        update_data = UpdateLeadRequest(email=other_lead.email)
        response = api_client.update_lead_raw(
            created_lead.id,
            update_data.model_dump(by_alias=True)
        )
        
        Assert.assert_status_range(response, 409, 422)
        
        # Cleanup
        api_client.delete_lead(other_lead.id)
