"""
Data Models for Lead Generation API
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, validator


class LeadStatus(str, Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(str, Enum):
    """Lead source enumeration"""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    PAID_ADS = "paid_ads"
    EVENT = "event"
    OTHER = "other"


class Address(BaseModel):
    """Address model"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias="postalCode")


class CreateLeadRequest(BaseModel):
    """Model for creating a new lead"""
    first_name: str = Field(..., min_length=1, max_length=100, alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=100, alias="lastName")
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s-]{10,}$')
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100, alias="jobTitle")
    source: LeadSource = LeadSource.WEBSITE
    status: LeadStatus = LeadStatus.NEW
    address: Optional[Address] = None
    notes: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = Field(None, alias="customFields")
    
    class Config:
        populate_by_name = True


class UpdateLeadRequest(BaseModel):
    """Model for updating an existing lead"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="firstName")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="lastName")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s-]{10,}$')
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100, alias="jobTitle")
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    address: Optional[Address] = None
    notes: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = Field(None, alias="customFields")
    
    class Config:
        populate_by_name = True


class LeadResponse(BaseModel):
    """Model for lead response"""
    id: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = Field(alias="jobTitle")
    source: str
    status: str
    address: Optional[Address] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    
    class Config:
        populate_by_name = True


class LeadListResponse(BaseModel):
    """Model for list leads response"""
    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")
    
    class Config:
        populate_by_name = True


class BulkImportRequest(BaseModel):
    """Model for bulk import request"""
    leads: List[CreateLeadRequest]
    skip_validation: bool = Field(False, alias="skipValidation")
    
    class Config:
        populate_by_name = True


class BulkImportResponse(BaseModel):
    """Model for bulk import response"""
    imported: int
    failed: int
    errors: Optional[List[dict]] = None
    
    
class LeadStatusResponse(BaseModel):
    """Model for lead status response"""
    lead_id: str = Field(alias="leadId")
    status: str
    previous_status: Optional[str] = Field(None, alias="previousStatus")
    updated_at: datetime = Field(alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
    
    class Config:
        populate_by_name = True


class ErrorResponse(BaseModel):
    """Model for API error response"""
    error: str
    message: str
    code: Optional[str] = None
    details: Optional[dict] = None
    timestamp: Optional[datetime] = None
    request_id: Optional[str] = Field(None, alias="requestId")
    
    class Config:
        populate_by_name = True


# JSON Schemas for validation
LEAD_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "firstName", "lastName", "email", "source", "status", "createdAt", "updatedAt"],
    "properties": {
        "id": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "phone": {"type": "string"},
        "company": {"type": "string"},
        "jobTitle": {"type": "string"},
        "source": {"type": "string"},
        "status": {"type": "string"},
        "notes": {"type": "string"},
        "createdAt": {"type": "string", "format": "date-time"},
        "updatedAt": {"type": "string", "format": "date-time"}
    }
}

LEAD_LIST_SCHEMA = {
    "type": "object",
    "required": ["leads", "total", "page", "pageSize"],
    "properties": {
        "leads": {
            "type": "array",
            "items": LEAD_RESPONSE_SCHEMA
        },
        "total": {"type": "integer"},
        "page": {"type": "integer"},
        "pageSize": {"type": "integer"}
    }
}
