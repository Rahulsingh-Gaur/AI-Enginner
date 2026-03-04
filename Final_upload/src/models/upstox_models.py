"""
Data Models for Upstox API
"""
from typing import Optional, Dict, Any, List, ClassVar
from pydantic import BaseModel, Field, field_validator


class GenerateOTPRequest(BaseModel):
    """Request model for Generate OTP API"""
    data: Dict[str, str] = Field(..., description="Request data container")
    
    @classmethod
    def with_mobile_number(cls, mobile_number: str) -> "GenerateOTPRequest":
        """Factory method to create request with mobile number"""
        return cls(data={"mobileNumber": mobile_number})


class GenerateOTPResponse(BaseModel):
    """Response model for Generate OTP API"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None  # For error responses
    errors: Optional[List[Dict[str, Any]]] = None  # Alternative error format
    request_id: Optional[str] = None  # Present in error responses
    
    @property
    def is_success(self) -> bool:
        """Check if response indicates success"""
        return self.success
    
    @property
    def validate_otp_token(self) -> Optional[str]:
        """Get validateOTPToken from response"""
        if self.data:
            return self.data.get("validateOTPToken")
        return None
    
    @property
    def message(self) -> str:
        """Get response message"""
        if self.data:
            return self.data.get("message", "")
        if self.error:
            return self.error.get("message", "Unknown error")
        if self.errors:
            return self.errors[0].get("message", "Unknown error")
        return ""
    
    @property
    def error_code(self) -> Optional[int]:
        """Get error code if present"""
        if self.error:
            return self.error.get("code")
        return None
    
    @property
    def next_request_interval(self) -> Optional[int]:
        """Get next request interval in seconds"""
        if self.data:
            return self.data.get("nextRequestInterval")
        return None


class UpstoxDeviceDetails(BaseModel):
    """Device details for headers"""
    platform: str = "WEB"
    device_id: str = Field(default="qaTestDevice123456", alias="deviceId")
    os_name: str = Field(default="iOS", alias="osName")
    os_version: str = Field(default="13.5.1", alias="osVersion")
    app_version: str = Field(default="2.3.14", alias="appVersion")
    imei: str = "000000000000"
    network: str = "net"
    memory: str = "mem"
    model_name: str = Field(default="iPhone101", alias="modelName")
    manufacturer: str = Field(default="Apple", alias="manufacturer")
    
    def to_header_string(self) -> str:
        """Convert to X-Device-Details header format"""
        return (
            f"platform={self.platform}|"
            f"deviceId={self.device_id}|"
            f"osName={self.os_name}|"
            f"osVersion={self.os_version}|"
            f"appVersion={self.app_version}|"
            f"imei={self.imei}|"
            f"network={self.network}|"
            f"memory={self.memory}|"
            f"modelName={self.model_name}|"
            f"manufacturer={self.manufacturer}"
        )
    
    class Config:
        populate_by_name = True


# Token storage for sharing between APIs
class TokenStore:
    """Singleton to store tokens and user data across API calls"""
    _instance = None
    _tokens: Dict[str, str] = {}
    _user_data: Dict[str, Any] = {}  # Store profileId, etc.
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenStore, cls).__new__(cls)
        return cls._instance
    
    def save_token(self, key: str, token: str):
        """Save token with key"""
        self._tokens[key] = token
    
    def get_token(self, key: str) -> Optional[str]:
        """Get token by key"""
        return self._tokens.get(key)
    
    def save_user_data(self, key: str, value: Any):
        """Save user data (profileId, etc.)"""
        self._user_data[key] = value
    
    def get_user_data(self, key: str) -> Optional[Any]:
        """Get user data by key"""
        return self._user_data.get(key)
    
    def clear_token(self, key: str):
        """Clear specific token"""
        if key in self._tokens:
            del self._tokens[key]
    
    def clear_user_data(self, key: str):
        """Clear specific user data"""
        if key in self._user_data:
            del self._user_data[key]
    
    def clear_all(self):
        """Clear all tokens and user data"""
        self._tokens.clear()
        self._user_data.clear()
    
    @property
    def all_tokens(self) -> Dict[str, str]:
        """Get all stored tokens"""
        return self._tokens.copy()
    
    @property
    def all_user_data(self) -> Dict[str, Any]:
        """Get all stored user data"""
        return self._user_data.copy()


class VerifyOTPRequest(BaseModel):
    """Request model for Verify OTP API"""
    data: Dict[str, str] = Field(..., description="Request data container")
    
    @classmethod
    def with_token_and_otp(cls, validate_otp_token: str, otp: str = "123789") -> "VerifyOTPRequest":
        """Factory method to create request with token and OTP"""
        return cls(data={
            "validateOtpToken": validate_otp_token,
            "otp": otp
        })


class VerifyOTPResponse(BaseModel):
    """Response model for Verify OTP API"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    request_id: Optional[str] = None
    
    # Expected success message (ClassVar so Pydantic ignores it)
    SUCCESS_MESSAGE: ClassVar[str] = "Your OTP has been successfully verified."
    
    @property
    def is_success(self) -> bool:
        """Check if response indicates success"""
        return self.success
    
    @property
    def message(self) -> str:
        """Get response message"""
        if self.data:
            return self.data.get("message", "")
        if self.error:
            return self.error.get("message", "Unknown error")
        if self.errors:
            return self.errors[0].get("message", "Unknown error")
        return ""
    
    @property
    def user_type(self) -> Optional[str]:
        """Get userType from response"""
        if self.data:
            return self.data.get("userType")
        return None
    
    @property
    def is_secret_pin_set(self) -> Optional[bool]:
        """Get isSecretPinSet from response"""
        if self.data:
            return self.data.get("isSecretPinSet")
        return None
    
    @property
    def profile_id(self) -> Optional[int]:
        """Get profileId from response (must be numeric)"""
        if self.data:
            # Try direct profileId first (for backward compatibility)
            profile_id = self.data.get("profileId")
            if profile_id is not None:
                try:
                    return int(profile_id)
                except (ValueError, TypeError):
                    pass
            
            # Try nested in userProfile (actual API structure)
            user_profile = self.data.get("userProfile")
            if user_profile and isinstance(user_profile, dict):
                profile_id = user_profile.get("profileId")
                if profile_id is not None:
                    try:
                        return int(profile_id)
                    except (ValueError, TypeError):
                        return None
        return None
    
    @property
    def error_code(self) -> Optional[int]:
        """Get error code if present"""
        if self.error:
            return self.error.get("code")
        if self.errors:
            return self.errors[0].get("code")
        return None
    
    def validate_success_response(self) -> tuple[bool, str]:
        """
        Validate all success criteria
        Returns: (is_valid, error_message)
        """
        if not self.success:
            return False, f"success is False: {self.message}"
        
        if not self.data:
            return False, "data is missing in response"
        
        # Validate message
        if self.message != self.SUCCESS_MESSAGE:
            return False, f"Message mismatch. Expected: '{self.SUCCESS_MESSAGE}', Got: '{self.message}'"
        
        # Validate userType
        if self.user_type != "LEAD":
            return False, f"userType mismatch. Expected: 'LEAD', Got: '{self.user_type}'"
        
        # Validate isSecretPinSet
        if self.is_secret_pin_set is not False:
            return False, f"isSecretPinSet mismatch. Expected: False, Got: {self.is_secret_pin_set}"
        
        # Validate profileId is numeric (check both direct and nested in userProfile)
        profile_id = self.profile_id
        if profile_id is None:
            # Check if userProfile exists for better error message
            if self.data.get("userProfile"):
                return False, "profileId is missing in userProfile"
            return False, "profileId is missing or not numeric"
        
        return True, "All validations passed"


# Error code constants
class UpstoxErrorCodes:
    """Upstox API error codes"""
    SESSION_EXPIRED = 1017076  # "Your session to validate otp has expired, please try again."
    RATE_LIMIT_EXCEEDED = 1017069
    INVALID_MOBILE = 1017016


# ═══════════════════════════════════════════════════════════════════
# PHASE 3: 2FA AUTHENTICATION API MODELS
# ═══════════════════════════════════════════════════════════════════

class TwoFactorAuthRequest(BaseModel):
    """Request model for 2FA Authentication API"""
    data: Dict[str, str] = Field(..., description="Request data container")
    
    @classmethod
    def with_token_and_otp(cls, validate_otp_token: str, otp: str = "123789") -> "TwoFactorAuthRequest":
        """Factory method to create 2FA request"""
        return cls(data={
            "validateOtpToken": validate_otp_token,
            "otp": otp
        })


class TwoFactorAuthResponse(BaseModel):
    """Response model for 2FA Authentication API"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    
    # Expected values for validation (ClassVar to exclude from Pydantic fields)
    EXPECTED_REDIRECT_URI: ClassVar[str] = "https://uat-pro.upstox.com"
    EXPECTED_USER_TYPE: ClassVar[str] = "LEAD"
    EXPECTED_CUSTOMER_STATUS: ClassVar[str] = "NEW"
    
    @property
    def is_success(self) -> bool:
        """Check if response indicates success"""
        return self.success
    
    @property
    def redirect_uri(self) -> Optional[str]:
        """Get redirectUri from response"""
        if self.data:
            return self.data.get("redirectUri")
        return None
    
    @property
    def user_type(self) -> Optional[str]:
        """Get userType from response"""
        if self.data:
            return self.data.get("userType")
        return None
    
    @property
    def customer_status(self) -> Optional[str]:
        """Get customerStatus from response"""
        if self.data:
            return self.data.get("customerStatus")
        return None
    
    @property
    def error_code(self) -> Optional[int]:
        """Get error code if present"""
        if self.error:
            return self.error.get("code")
        if self.errors:
            return self.errors[0].get("code")
        return None
    
    @property
    def message(self) -> str:
        """Get response message"""
        if self.data:
            return self.data.get("message", "")
        if self.error:
            return self.error.get("message", "Unknown error")
        if self.errors:
            return self.errors[0].get("message", "Unknown error")
        return ""
    
    def validate_success_response(self) -> tuple[bool, str]:
        """
        Validate all 2FA success criteria
        Returns: (is_valid, error_message)
        """
        if not self.success:
            return False, f"success is False: {self.message}"
        
        if not self.data:
            return False, "data is missing in response"
        
        # Validate redirectUri
        if self.redirect_uri != self.EXPECTED_REDIRECT_URI:
            return False, f"redirectUri mismatch. Expected: '{self.EXPECTED_REDIRECT_URI}', Got: '{self.redirect_uri}'"
        
        # Validate userType
        if self.user_type != self.EXPECTED_USER_TYPE:
            return False, f"userType mismatch. Expected: '{self.EXPECTED_USER_TYPE}', Got: '{self.user_type}'"
        
        # Validate customerStatus
        if self.customer_status != self.EXPECTED_CUSTOMER_STATUS:
            return False, f"customerStatus mismatch. Expected: '{self.EXPECTED_CUSTOMER_STATUS}', Got: '{self.customer_status}'"
        
        return True, "All 2FA validations passed"


# ═══════════════════════════════════════════════════════════════════
# PHASE 4: EMAIL SEND OTP API MODELS
# ═══════════════════════════════════════════════════════════════════

class EmailSendOTPRequest(BaseModel):
    """Request model for Email Send OTP API"""
    email: str = Field(..., description="Email address to send OTP")
    
    @classmethod
    def with_email(cls, email: str) -> "EmailSendOTPRequest":
        """Factory method to create request with email"""
        return cls(email=email)
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email ends with _@gmail.com"""
        if not v.endswith("_@gmail.com"):
            raise ValueError(f"Email must end with '_@gmail.com', got: {v}")
        return v


class EmailSendOTPResponse(BaseModel):
    """Response model for Email Send OTP API"""
    # The response is flat: {"EMAIL": "OTP sent successfully"}
    # No 'success' field or 'data' wrapper in actual API response
    
    # Make all fields optional since response is flat
    success: Optional[bool] = None  # Not present in actual response
    data: Optional[Dict[str, Any]] = None  # Not used in actual response
    error: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    
    # Store raw response for flat parsing
    _raw_response: Optional[Dict[str, Any]] = None
    
    # Expected success message
    EXPECTED_MESSAGE: ClassVar[str] = "OTP sent successfully"
    EXPECTED_KEY: ClassVar[str] = "EMAIL"
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to handle flat response"""
        # If no success field but has EMAIL key, it's a success response
        if self.success is None and self.data is None:
            # This is a flat response, treat as success if EMAIL key exists
            pass
    
    @property
    def is_success(self) -> bool:
        """Check if response indicates success - EMAIL key present"""
        # Success if EMAIL key exists with expected message
        return self.message == self.EXPECTED_MESSAGE
    
    @property
    def message(self) -> Optional[str]:
        """Get message from response - handle flat and wrapped formats"""
        # Check flat response first (actual API format)
        if hasattr(self, '_raw_response') and self._raw_response:
            return self._raw_response.get(self.EXPECTED_KEY)
        # Check in data wrapper (if wrapped)
        if self.data:
            return self.data.get(self.EXPECTED_KEY)
        return None
    
    @property
    def error_message(self) -> str:
        """Get error message if any"""
        if self.error:
            return self.error.get("message", "Unknown error")
        if self.errors:
            return self.errors[0].get("message", "Unknown error")
        return ""
    
    @property
    def error_code(self) -> Optional[int]:
        """Get error code if present"""
        if self.error:
            return self.error.get("code")
        if self.errors:
            return self.errors[0].get("code")
        return None
    
    def validate_success_response(self) -> tuple[bool, str]:
        """
        Validate Email OTP success criteria
        Required: {"EMAIL": "OTP sent successfully"}
        
        Returns: (is_valid, error_message)
        """
        # Check if EMAIL key exists
        actual_message = self.message
        
        if actual_message is None:
            return False, f"Missing '{self.EXPECTED_KEY}' key in response"
        
        # Validate message value
        if actual_message != self.EXPECTED_MESSAGE:
            return False, f"Message mismatch. Expected: '{self.EXPECTED_MESSAGE}', Got: '{actual_message}'"
        
        return True, "Email OTP validation passed"
    
    @classmethod
    def from_raw_response(cls, raw_data: Dict[str, Any]) -> "EmailSendOTPResponse":
        """
        Factory method to create response from raw API response.
        Handles flat format: {"EMAIL": "OTP sent successfully"}
        """
        instance = cls(
            success=raw_data.get("success"),  # May be None
            data=raw_data.get("data"),  # May be None
            error=raw_data.get("error"),
            errors=raw_data.get("errors")
        )
        instance._raw_response = raw_data
        return instance


# ═══════════════════════════════════════════════════════════════════
# PHASE 5: EMAIL VERIFY OTP API MODELS
# ═══════════════════════════════════════════════════════════════════

class EmailVerifyOTPRequest(BaseModel):
    """Request model for Email Verify OTP API"""
    email: str = Field(..., description="Email address to verify")
    otp: str = Field(default="123789", description="OTP code to verify")
    
    @classmethod
    def with_email_and_otp(cls, email: str, otp: str = "123789") -> "EmailVerifyOTPRequest":
        """Factory method to create request with email and OTP"""
        return cls(email=email, otp=otp)


class EmailVerifyOTPResponse(BaseModel):
    """Response model for Email Verify OTP API"""
    # Flat response format: {"EMAIL": "OTP verified successfully"}
    success: Optional[bool] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    
    # Store raw response for flat parsing
    _raw_response: Optional[Dict[str, Any]] = None
    
    # Expected success message
    EXPECTED_MESSAGE: ClassVar[str] = "OTP verified successfully"
    EXPECTED_KEY: ClassVar[str] = "EMAIL"
    
    @property
    def is_success(self) -> bool:
        """Check if response indicates success - EMAIL key present with expected message"""
        return self.message == self.EXPECTED_MESSAGE
    
    @property
    def message(self) -> Optional[str]:
        """Get message from response - handle flat and wrapped formats"""
        # Check flat response first
        if hasattr(self, '_raw_response') and self._raw_response:
            return self._raw_response.get(self.EXPECTED_KEY)
        # Check in data wrapper (if wrapped)
        if self.data:
            return self.data.get(self.EXPECTED_KEY)
        return None
    
    @property
    def error_message(self) -> str:
        """Get error message if any"""
        if self.error:
            return self.error.get("message", "Unknown error")
        if self.errors:
            return self.errors[0].get("message", "Unknown error")
        return ""
    
    def validate_success_response(self) -> tuple[bool, str]:
        """
        Validate Email Verify OTP success criteria
        Required: {"EMAIL": "OTP verified successfully"}
        
        Returns: (is_valid, error_message)
        """
        # Check if EMAIL key exists
        actual_message = self.message
        
        if actual_message is None:
            return False, f"Missing '{self.EXPECTED_KEY}' key in response"
        
        # Validate message value
        if actual_message != self.EXPECTED_MESSAGE:
            return False, f"Message mismatch. Expected: '{self.EXPECTED_MESSAGE}', Got: '{actual_message}'"
        
        return True, "Email OTP verification passed"
    
    @classmethod
    def from_raw_response(cls, raw_data: Dict[str, Any]) -> "EmailVerifyOTPResponse":
        """
        Factory method to create response from raw API response.
        Handles flat format: {"EMAIL": "OTP verified successfully"}
        """
        instance = cls(
            success=raw_data.get("success"),
            data=raw_data.get("data"),
            error=raw_data.get("error"),
            errors=raw_data.get("errors")
        )
        instance._raw_response = raw_data
        return instance


# Global token store instance
token_store = TokenStore()
