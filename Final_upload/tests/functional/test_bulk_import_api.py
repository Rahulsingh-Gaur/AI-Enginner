"""
Test Cases for Bulk Import API (POST /api/v1/leads/bulk-import)
"""
import pytest
from src.models.lead_models import CreateLeadRequest
from src.utils.assertions import APIAssertions as Assert


@pytest.mark.bulk
@pytest.mark.smoke
@pytest.mark.positive
class TestBulkImportAPI:
    """Positive test cases for Bulk Import API"""
    
    def test_bulk_import_single_lead(self, api_client, sample_lead_data):
        """TC-048: Bulk import single lead"""
        response = api_client.bulk_import([sample_lead_data])
        
        assert response.imported == 1
        assert response.failed == 0
    
    def test_bulk_import_multiple_leads(self, api_client):
        """TC-049: Bulk import multiple leads"""
        from faker import Faker
        import uuid
        
        faker = Faker()
        leads = []
        
        for i in range(5):
            leads.append(CreateLeadRequest(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=f"bulk_{uuid.uuid4().hex[:8]}@example.com"
            ))
        
        response = api_client.bulk_import(leads)
        
        assert response.imported == 5
        assert response.failed == 0
    
    def test_bulk_import_large_batch(self, api_client):
        """TC-050: Bulk import large batch of leads"""
        from faker import Faker
        import uuid
        
        faker = Faker()
        leads = []
        
        for i in range(50):
            leads.append(CreateLeadRequest(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=f"batch_{uuid.uuid4().hex[:8]}_{i}@example.com"
            ))
        
        response = api_client.bulk_import(leads)
        
        assert response.imported == 50


@pytest.mark.bulk
@pytest.mark.negative
class TestBulkImportAPINegative:
    """Negative test cases for Bulk Import API"""
    
    def test_bulk_import_empty_list(self, api_client):
        """TC-051: Bulk import empty list"""
        response = api_client.bulk_import_raw({"leads": []})
        Assert.assert_status_range(response, 400, 422)
    
    def test_bulk_import_duplicate_emails(self, api_client, unique_email):
        """TC-052: Bulk import with duplicate emails in batch"""
        leads = [
            CreateLeadRequest(
                first_name="John",
                last_name="Doe",
                email=unique_email
            ),
            CreateLeadRequest(
                first_name="Jane",
                last_name="Doe",
                email=unique_email  # Same email
            )
        ]
        
        response = api_client.bulk_import(leads)
        
        # Should import 1 and fail 1
        assert response.imported == 1
        assert response.failed == 1
    
    def test_bulk_import_exceeds_limit(self, api_client):
        """TC-053: Bulk import exceeds maximum batch size"""
        from faker import Faker
        import uuid
        
        faker = Faker()
        leads = []
        
        # Create more than allowed (assuming limit is 100)
        for i in range(150):
            leads.append({
                "firstName": faker.first_name(),
                "lastName": faker.last_name(),
                "email": f"limit_{uuid.uuid4().hex}@example.com"
            })
        
        response = api_client.bulk_import_raw({"leads": leads})
        Assert.assert_status_range(response, 400, 422)
    
    def test_bulk_import_invalid_lead_data(self, api_client):
        """TC-054: Bulk import with invalid lead data"""
        response = api_client.bulk_import_raw({
            "leads": [
                {"firstName": "John"},  # Missing required fields
                {"firstName": "Jane", "lastName": "Doe"}  # Missing email
            ]
        })
        
        result = response.json()
        assert result["failed"] > 0


@pytest.mark.bulk
@pytest.mark.performance
class TestBulkImportAPIPerformance:
    """Performance tests for Bulk Import API"""
    
    def test_bulk_import_response_time(self, api_client):
        """TC-055: Bulk import response time for 100 leads"""
        from faker import Faker
        import uuid
        
        faker = Faker()
        leads = [
            CreateLeadRequest(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=f"perf_{uuid.uuid4().hex[:8]}_{i}@example.com"
            )
            for i in range(100)
        ]
        
        response = api_client.http.post(
            api_client.BULK_IMPORT,
            json={"leads": [l.model_dump(by_alias=True) for l in leads]}
        )
        
        # Should complete within 10 seconds
        Assert.assert_response_time(response, 10000)
