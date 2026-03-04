"""
Lead Generation API Client
Implements all 7 Lead Generation API endpoints
"""
from typing import List, Optional, Dict, Any
import requests

from src.api_clients.base_client import BaseAPIClient
from src.models.lead_models import (
    CreateLeadRequest,
    UpdateLeadRequest,
    LeadResponse,
    LeadListResponse,
    LeadStatusResponse,
    BulkImportRequest,
    BulkImportResponse,
    LEAD_RESPONSE_SCHEMA,
    LEAD_LIST_SCHEMA
)
from src.utils.assertions import APIAssertions
from src.utils.logger import logger


class LeadAPIClient(BaseAPIClient):
    """
    Client for Lead Generation APIs
    
    Endpoints:
    1. POST   /api/v1/leads              - Create Lead
    2. GET    /api/v1/leads/{lead_id}    - Get Lead
    3. PUT    /api/v1/leads/{lead_id}    - Update Lead
    4. DELETE /api/v1/leads/{lead_id}    - Delete Lead
    5. GET    /api/v1/leads              - List Leads
    6. GET    /api/v1/leads/{lead_id}/status - Get Lead Status
    7. POST   /api/v1/leads/bulk-import  - Bulk Import Leads
    """
    
    # API Endpoints
    CREATE_LEAD = "/api/v1/leads"
    GET_LEAD = "/api/v1/leads/{lead_id}"
    UPDATE_LEAD = "/api/v1/leads/{lead_id}"
    DELETE_LEAD = "/api/v1/leads/{lead_id}"
    LIST_LEADS = "/api/v1/leads"
    LEAD_STATUS = "/api/v1/leads/{lead_id}/status"
    BULK_IMPORT = "/api/v1/leads/bulk-import"
    
    # ═══════════════════════════════════════════════════════════════
    # 1. CREATE LEAD
    # ═══════════════════════════════════════════════════════════════
    def create_lead(
        self,
        lead_data: CreateLeadRequest,
        validate_response: bool = True
    ) -> LeadResponse:
        """
        Create a new lead
        
        Args:
            lead_data: Lead creation data
            validate_response: Whether to validate response schema
            
        Returns:
            LeadResponse object
        """
        logger.info(f"Creating lead: {lead_data.email}")
        
        response = self.http.post(
            self.CREATE_LEAD,
            json=lead_data.model_dump(by_alias=True, exclude_none=True)
        )
        
        if validate_response:
            APIAssertions.assert_json_schema(response, LEAD_RESPONSE_SCHEMA)
        
        return self._handle_response(response, LeadResponse)
    
    def create_lead_raw(self, lead_dict: Dict[str, Any]) -> requests.Response:
        """Create lead with raw dictionary data (for negative testing)"""
        return self.http.post(self.CREATE_LEAD, json=lead_dict)
    
    # ═══════════════════════════════════════════════════════════════
    # 2. GET LEAD
    # ═══════════════════════════════════════════════════════════════
    def get_lead(
        self,
        lead_id: str,
        validate_response: bool = True
    ) -> LeadResponse:
        """
        Get lead by ID
        
        Args:
            lead_id: Lead identifier
            validate_response: Whether to validate response schema
            
        Returns:
            LeadResponse object
        """
        logger.info(f"Fetching lead: {lead_id}")
        
        url = self._build_url(self.GET_LEAD, lead_id=lead_id)
        response = self.http.get(url)
        
        if validate_response:
            APIAssertions.assert_json_schema(response, LEAD_RESPONSE_SCHEMA)
        
        return self._handle_response(response, LeadResponse)
    
    def get_lead_raw(self, lead_id: str) -> requests.Response:
        """Get lead raw response (for error testing)"""
        url = self._build_url(self.GET_LEAD, lead_id=lead_id)
        return self.http.get(url)
    
    # ═══════════════════════════════════════════════════════════════
    # 3. UPDATE LEAD
    # ═══════════════════════════════════════════════════════════════
    def update_lead(
        self,
        lead_id: str,
        update_data: UpdateLeadRequest,
        validate_response: bool = True
    ) -> LeadResponse:
        """
        Update existing lead
        
        Args:
            lead_id: Lead identifier
            update_data: Lead update data
            validate_response: Whether to validate response schema
            
        Returns:
            LeadResponse object
        """
        logger.info(f"Updating lead: {lead_id}")
        
        url = self._build_url(self.UPDATE_LEAD, lead_id=lead_id)
        response = self.http.put(
            url,
            json=update_data.model_dump(by_alias=True, exclude_none=True)
        )
        
        if validate_response:
            APIAssertions.assert_json_schema(response, LEAD_RESPONSE_SCHEMA)
        
        return self._handle_response(response, LeadResponse)
    
    def update_lead_raw(
        self,
        lead_id: str,
        update_dict: Dict[str, Any]
    ) -> requests.Response:
        """Update lead with raw dictionary (for negative testing)"""
        url = self._build_url(self.UPDATE_LEAD, lead_id=lead_id)
        return self.http.put(url, json=update_dict)
    
    # ═══════════════════════════════════════════════════════════════
    # 4. DELETE LEAD
    # ═══════════════════════════════════════════════════════════════
    def delete_lead(self, lead_id: str) -> bool:
        """
        Delete lead by ID
        
        Args:
            lead_id: Lead identifier
            
        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting lead: {lead_id}")
        
        url = self._build_url(self.DELETE_LEAD, lead_id=lead_id)
        response = self.http.delete(url)
        
        return response.status_code in [200, 204]
    
    def delete_lead_raw(self, lead_id: str) -> requests.Response:
        """Delete lead raw response (for testing)"""
        url = self._build_url(self.DELETE_LEAD, lead_id=lead_id)
        return self.http.delete(url)
    
    # ═══════════════════════════════════════════════════════════════
    # 5. LIST LEADS
    # ═══════════════════════════════════════════════════════════════
    def list_leads(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
        validate_response: bool = True
    ) -> LeadListResponse:
        """
        List leads with pagination and filtering
        
        Args:
            page: Page number
            page_size: Items per page
            status: Filter by status
            source: Filter by source
            search: Search query
            validate_response: Whether to validate response schema
            
        Returns:
            LeadListResponse object
        """
        logger.info(f"Listing leads - page: {page}, size: {page_size}")
        
        params = {
            "page": page,
            "pageSize": page_size
        }
        
        if status:
            params["status"] = status
        if source:
            params["source"] = source
        if search:
            params["search"] = search
        
        response = self.http.get(self.LIST_LEADS, params=params)
        
        if validate_response:
            APIAssertions.assert_json_schema(response, LEAD_LIST_SCHEMA)
        
        return self._handle_response(response, LeadListResponse)
    
    def list_leads_raw(self, **params) -> requests.Response:
        """List leads raw response (for testing)"""
        return self.http.get(self.LIST_LEADS, params=params)
    
    # ═══════════════════════════════════════════════════════════════
    # 6. GET LEAD STATUS
    # ═══════════════════════════════════════════════════════════════
    def get_lead_status(
        self,
        lead_id: str,
        validate_response: bool = True
    ) -> LeadStatusResponse:
        """
        Get lead status
        
        Args:
            lead_id: Lead identifier
            validate_response: Whether to validate response schema
            
        Returns:
            LeadStatusResponse object
        """
        logger.info(f"Fetching status for lead: {lead_id}")
        
        url = self._build_url(self.LEAD_STATUS, lead_id=lead_id)
        response = self.http.get(url)
        
        return self._handle_response(response, LeadStatusResponse)
    
    def get_lead_status_raw(self, lead_id: str) -> requests.Response:
        """Get lead status raw response (for testing)"""
        url = self._build_url(self.LEAD_STATUS, lead_id=lead_id)
        return self.http.get(url)
    
    # ═══════════════════════════════════════════════════════════════
    # 7. BULK IMPORT LEADS
    # ═══════════════════════════════════════════════════════════════
    def bulk_import(
        self,
        leads: List[CreateLeadRequest],
        skip_validation: bool = False,
        validate_response: bool = True
    ) -> BulkImportResponse:
        """
        Bulk import leads
        
        Args:
            leads: List of lead data
            skip_validation: Skip validation on server side
            validate_response: Whether to validate response
            
        Returns:
            BulkImportResponse object
        """
        logger.info(f"Bulk importing {len(leads)} leads")
        
        request_data = BulkImportRequest(
            leads=leads,
            skipValidation=skip_validation
        )
        
        response = self.http.post(
            self.BULK_IMPORT,
            json=request_data.model_dump(by_alias=True, exclude_none=True)
        )
        
        return self._handle_response(response, BulkImportResponse)
    
    def bulk_import_raw(self, data: Dict[str, Any]) -> requests.Response:
        """Bulk import raw data (for testing)"""
        return self.http.post(self.BULK_IMPORT, json=data)
    
    # ═══════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════
    def lead_exists(self, lead_id: str) -> bool:
        """Check if lead exists"""
        try:
            response = self.get_lead_raw(lead_id)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_lead(
        self,
        lead_id: str,
        expected_status: Optional[str] = None,
        timeout: int = 30,
        interval: float = 1.0
    ) -> Optional[LeadResponse]:
        """
        Wait for lead to be available (useful for async operations)
        
        Args:
            lead_id: Lead identifier
            expected_status: Expected status to wait for
            timeout: Maximum wait time in seconds
            interval: Polling interval
            
        Returns:
            LeadResponse when found, None if timeout
        """
        import time
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                lead = self.get_lead(lead_id, validate_response=False)
                if expected_status is None or lead.status == expected_status:
                    return lead
            except:
                pass
            time.sleep(interval)
        
        return None
