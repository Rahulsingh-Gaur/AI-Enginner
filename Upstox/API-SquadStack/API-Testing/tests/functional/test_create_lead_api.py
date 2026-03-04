"""
Test Cases for Create Lead API (POST /api/v1/leads)
"""
import pytest
from src.models.lead_models import CreateLeadRequest, LeadSource, LeadStatus
from src.utils.assertions import APIAssertions as Assert
from src.utils.logger import logger


@pytest.mark.create
@pytest.mark.smoke
@pytest.mark.positive
class TestCreateLeadAPI:
    """Positive test cases for Create Lead API"""
    
    def test_create_lead_with_valid_data(self, api_client, sample_lead_data):
        """TC-001: Create lead with all valid data"""
        logger.info("Testing create lead with valid data...")
        
        response = api_client.create_lead(sample_lead_data)
        
        assert response.id is not None
        assert response.email == sample_lead_data.email
        assert response.first_name == sample_lead_data.first_name
        assert response.last_name == sample_lead_data.last_name
        assert response.status == LeadStatus.NEW.value
        
        # Cleanup
        api_client.delete_lead(response.id)
    
    def test_create_lead_with_minimal_data(self, api_client, unique_email):
        """TC-002: Create lead with minimal required fields"""
        data = CreateLeadRequest(
            first_name="John",
            last_name="Doe",
            email=unique_email
        )
        
        response = api_client.create_lead(data)
        
        assert response.id is not None
        assert response.email == unique_email
        
        # Cleanup
        api_client.delete_lead(response.id)
    
    def test_create_lead_response_schema(self, api_client, sample_lead_data):
        """TC-003: Verify create lead response schema"""
        response = api_client.http.post(
            api_client.CREATE_LEAD,
            json=sample_lead_data.model_dump(by_alias=True)
        )
        
        Assert.assert_status_code(response, 201)
        Assert.assert_content_type(response, "application/json")
        Assert.assert_json_contains(response, "id")
        Assert.assert_json_contains(response, "createdAt")
        Assert.assert_json_contains(response, "updatedAt")
    
    def test_create_lead_response_time(self, api_client, sample_lead_data):
        """TC-004: Verify create lead response time under 2 seconds"""
        response = api_client.http.post(
            api_client.CREATE_LEAD,
            json=sample_lead_data.model_dump(by_alias=True)
        )
        
        Assert.assert_response_time(response, 2000)  # 2 seconds
    
    def test_create_lead_with_all_sources(self, api_client, unique_email):
        """TC-005: Create leads with all possible sources"""
        created_ids = []
        
        for source in LeadSource:
            data = CreateLeadRequest(
                first_name="Test",
                last_name="User",
                email=f"{source.value}_{unique_email}",
                source=source
            )
            
            response = api_client.create_lead(data)
            assert response.source == source.value
            created_ids.append(response.id)
        
        # Cleanup
        for lead_id in created_ids:
            api_client.delete_lead(lead_id)


@pytest.mark.create
@pytest.mark.negative
class TestCreateLeadAPINegative:
    """Negative test cases for Create Lead API"""
    
    def test_create_lead_with_duplicate_email(self, api_client, created_lead):
        """TC-006: Create lead with duplicate email should fail"""
        duplicate_data = CreateLeadRequest(
            first_name="Another",
            last_name="User",
            email=created_lead.email
        )
        
        response = api_client.create_lead_raw(
            duplicate_data.model_dump(by_alias=True)
        )
        
        Assert.assert_status_range(response, 400, 409)
    
    def test_create_lead_without_email(self, api_client):
        """TC-007: Create lead without email should fail"""
        invalid_data = {
            "firstName": "John",
            "lastName": "Doe"
            # email is missing
        }
        
        response = api_client.create_lead_raw(invalid_data)
        Assert.assert_status_range(response, 400, 422)
    
    def test_create_lead_with_invalid_email(self, api_client):
        """TC-008: Create lead with invalid email format"""
        invalid_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "invalid-email-format"
        }
        
        response = api_client.create_lead_raw(invalid_data)
        Assert.assert_status_range(response, 400, 422)
    
    def test_create_lead_without_first_name(self, api_client, unique_email):
        """TC-009: Create lead without first name should fail"""
        invalid_data = {
            "lastName": "Doe",
            "email": unique_email
        }
        
        response = api_client.create_lead_raw(invalid_data)
        Assert.assert_status_range(response, 400, 422)
    
    def test_create_lead_with_long_first_name(self, api_client, unique_email):
        """TC-010: Create lead with first name exceeding max length"""
        invalid_data = {
            "firstName": "A" * 101,  # Assuming max is 100
            "lastName": "Doe",
            "email": unique_email
        }
        
        response = api_client.create_lead_raw(invalid_data)
        Assert.assert_status_range(response, 400, 422)
    
    def test_create_lead_unauthorized(self, api_client):
        """TC-011: Create lead without authentication should fail"""
        # This would need a client without auth
        pass  # Implement based on auth requirements


@pytest.mark.create
@pytest.mark.regression
class TestCreateLeadAPIEdgeCases:
    """Edge case tests for Create Lead API"""
    
    def test_create_lead_with_special_characters(self, api_client, unique_email):
        """TC-012: Create lead with special characters in name"""
        data = CreateLeadRequest(
            first_name="John@#$%",
            last_name="O'Connor-Smith",
            email=unique_email
        )
        
        response = api_client.create_lead(data)
        assert response.id is not None
        
        api_client.delete_lead(response.id)
    
    def test_create_lead_with_unicode(self, api_client, unique_email):
        """TC-013: Create lead with unicode characters"""
        data = CreateLeadRequest(
            first_name="José",
            last_name="日本語",
            email=unique_email
        )
        
        response = api_client.create_lead(data)
        assert response.id is not None
        
        api_client.delete_lead(response.id)
    
    def test_create_lead_with_xss_attempt(self, api_client, unique_email):
        """TC-014: Create lead with XSS attempt should be sanitized"""
        data = CreateLeadRequest(
            first_name="<script>alert('xss')</script>",
            last_name="Doe",
            email=unique_email
        )
        
        response = api_client.create_lead(data)
        
        # Verify XSS is sanitized
        assert "<script>" not in response.first_name
        
        api_client.delete_lead(response.id)
