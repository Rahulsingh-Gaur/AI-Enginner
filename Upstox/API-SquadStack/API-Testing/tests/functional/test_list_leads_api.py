"""
Test Cases for List Leads API (GET /api/v1/leads)
"""
import pytest
from src.utils.assertions import APIAssertions as Assert


@pytest.mark.list
@pytest.mark.smoke
@pytest.mark.positive
class TestListLeadsAPI:
    """Positive test cases for List Leads API"""
    
    def test_list_leads_default_pagination(self, api_client, multiple_leads):
        """TC-033: List leads with default pagination"""
        response = api_client.list_leads()
        
        assert response.total > 0
        assert len(response.leads) > 0
        assert response.page == 1
    
    def test_list_leads_custom_pagination(self, api_client, multiple_leads):
        """TC-034: List leads with custom page size"""
        response = api_client.list_leads(page=1, page_size=2)
        
        assert len(response.leads) <= 2
        assert response.page_size == 2
    
    def test_list_leads_second_page(self, api_client, multiple_leads):
        """TC-035: List leads - second page"""
        response = api_client.list_leads(page=2, page_size=2)
        
        assert response.page == 2
    
    def test_list_leads_filter_by_status(self, api_client, multiple_leads):
        """TC-036: List leads filtered by status"""
        response = api_client.list_leads(status="new")
        
        for lead in response.leads:
            assert lead.status == "new"
    
    def test_list_leads_filter_by_source(self, api_client, multiple_leads):
        """TC-037: List leads filtered by source"""
        response = api_client.list_leads(source="website")
        
        for lead in response.leads:
            assert lead.source == "website"
    
    def test_list_leads_search(self, api_client, multiple_leads):
        """TC-038: Search leads"""
        # Search by first name of first lead
        search_term = multiple_leads[0].first_name
        response = api_client.list_leads(search=search_term)
        
        assert response.total >= 1


@pytest.mark.list
@pytest.mark.negative
class TestListLeadsAPINegative:
    """Negative test cases for List Leads API"""
    
    def test_list_leads_invalid_page(self, api_client):
        """TC-039: List leads with invalid page number"""
        response = api_client.list_leads_raw(page=-1)
        Assert.assert_status_range(response, 400, 422)
    
    def test_list_leads_invalid_page_size(self, api_client):
        """TC-040: List leads with invalid page size"""
        response = api_client.list_leads_raw(page_size=0)
        Assert.assert_status_range(response, 400, 422)
    
    def test_list_leads_page_size_too_large(self, api_client):
        """TC-041: List leads with page size exceeding limit"""
        response = api_client.list_leads_raw(page_size=10000)
        Assert.assert_status_range(response, 400, 422)
    
    def test_list_leads_invalid_status(self, api_client):
        """TC-042: List leads with invalid status filter"""
        response = api_client.list_leads_raw(status="invalid_status")
        Assert.assert_status_range(response, 400, 422)


@pytest.mark.list
@pytest.mark.performance
class TestListLeadsAPIPerformance:
    """Performance tests for List Leads API"""
    
    def test_list_leads_response_time(self, api_client):
        """TC-043: List leads response time under 1 second"""
        response = api_client.list_leads_raw()
        Assert.assert_response_time(response, 1000)
