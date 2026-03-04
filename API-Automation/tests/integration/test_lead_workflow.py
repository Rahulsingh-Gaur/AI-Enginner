"""
Integration Tests - Lead Workflow
Tests complete user workflows across multiple APIs
"""
import pytest
from src.models.lead_models import CreateLeadRequest, UpdateLeadRequest, LeadStatus, LeadSource


@pytest.mark.integration
class TestLeadWorkflow:
    """End-to-end lead management workflow tests"""
    
    def test_complete_lead_lifecycle(self, api_client):
        """
        TC-I001: Complete lead lifecycle
        Create → Read → Update → Status Check → Delete
        """
        # 1. Create lead
        create_data = CreateLeadRequest(
            first_name="Workflow",
            last_name="Test",
            email=f"workflow_{uuid.uuid4()}@example.com",
            source=LeadSource.WEBSITE,
            status=LeadStatus.NEW
        )
        lead = api_client.create_lead(create_data)
        assert lead.status == LeadStatus.NEW.value
        
        # 2. Read lead
        fetched_lead = api_client.get_lead(lead.id)
        assert fetched_lead.id == lead.id
        assert fetched_lead.email == lead.email
        
        # 3. Update lead status
        update_data = UpdateLeadRequest(status=LeadStatus.QUALIFIED)
        updated_lead = api_client.update_lead(lead.id, update_data)
        assert updated_lead.status == LeadStatus.QUALIFIED.value
        
        # 4. Check status
        status = api_client.get_lead_status(lead.id)
        assert status.status == LeadStatus.QUALIFIED.value
        assert status.previous_status == LeadStatus.NEW.value
        
        # 5. Delete lead
        deleted = api_client.delete_lead(lead.id)
        assert deleted is True
        
        # 6. Verify deletion
        response = api_client.get_lead_raw(lead.id)
        assert response.status_code == 404
    
    def test_bulk_import_and_list_workflow(self, api_client):
        """
        TC-I002: Bulk import workflow
        Bulk Import → List → Verify Count → Cleanup
        """
        import uuid
        from faker import Faker
        
        faker = Faker()
        
        # 1. Get initial count
        initial_list = api_client.list_leads()
        initial_count = initial_list.total
        
        # 2. Bulk import
        leads_to_import = [
            CreateLeadRequest(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=f"bulk_{uuid.uuid4().hex[:8]}@example.com"
            )
            for _ in range(10)
        ]
        
        import_result = api_client.bulk_import(leads_to_import)
        assert import_result.imported == 10
        assert import_result.failed == 0
        
        # 3. Verify count increased
        updated_list = api_client.list_leads()
        assert updated_list.total >= initial_count + 10
        
        # 4. Verify leads appear in list
        found_count = 0
        for lead in leads_to_import:
            list_result = api_client.list_leads(search=lead.email)
            if list_result.total > 0:
                found_count += 1
        
        assert found_count == 10
    
    def test_lead_status_transitions(self, api_client, sample_lead_data):
        """
        TC-I003: Lead status transitions
        Test all valid status transitions
        """
        # Create lead
        lead = api_client.create_lead(sample_lead_data)
        
        transitions = [
            (LeadStatus.NEW, LeadStatus.CONTACTED),
            (LeadStatus.CONTACTED, LeadStatus.QUALIFIED),
            (LeadStatus.QUALIFIED, LeadStatus.CONVERTED),
        ]
        
        for from_status, to_status in transitions:
            # Update status
            update_data = UpdateLeadRequest(status=to_status)
            updated = api_client.update_lead(lead.id, update_data)
            assert updated.status == to_status.value
            
            # Check status history
            status_info = api_client.get_lead_status(lead.id)
            assert status_info.status == to_status.value
        
        # Cleanup
        api_client.delete_lead(lead.id)
