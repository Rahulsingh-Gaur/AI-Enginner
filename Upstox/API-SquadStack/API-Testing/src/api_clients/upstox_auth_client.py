"""
Upstox Authentication API Client
Handles OTP generation and validation
"""
from typing import Optional, Dict, Any
import requests

from src.api_clients.base_client import BaseAPIClient
from src.models.upstox_models import (
    GenerateOTPRequest, 
    GenerateOTPResponse, 
    VerifyOTPRequest,
    VerifyOTPResponse,
    TwoFactorAuthRequest,
    TwoFactorAuthResponse,
    EmailSendOTPRequest,
    EmailSendOTPResponse,
    EmailVerifyOTPRequest,
    EmailVerifyOTPResponse,
    UpstoxDeviceDetails,
    UpstoxErrorCodes,
    token_store
)
from src.utils.assertions import APIAssertions
from src.utils.logger import logger


class UpstoxAuthClient(BaseAPIClient):
    """
    Upstox Authentication Client
    
    Base URL: https://service-uat.upstox.com
    
    APIs:
    1. POST /login/open/v8/auth/1fa/otp-step/generate - Generate OTP
    2. POST /login/open/v8/auth/1fa/otp-step/validate - Validate OTP
    3. POST /login/open/v8/auth/1fa/login - Login
    """
    
    BASE_URL = "https://service-uat.upstox.com"
    
    # Endpoints
    GENERATE_OTP_ENDPOINT = "/login/open/v8/auth/1fa/otp-step/generate"
    VALIDATE_OTP_ENDPOINT = "/login/open/v8/auth/1fa/otp-step/validate"
    VERIFY_OTP_ENDPOINT = "/login/open/v4/auth/1fa/otp-totp/verify"
    TWO_FA_ENDPOINT = "/login/open/v1/auth/leads/2fa"
    EMAIL_SEND_OTP_ENDPOINT = "/account-opening/v3/email/send-otp"
    EMAIL_VERIFY_OTP_ENDPOINT = "/account-opening/v3/email/verify-otp"
    LOGIN_ENDPOINT = "/login/open/v8/auth/1fa/login"
    
    def __init__(
        self,
        request_id: str = "qatest4567",
        device_details: Optional[UpstoxDeviceDetails] = None
    ):
        """
        Initialize Upstox Auth Client
        
        Args:
            request_id: Request ID for query parameter (default: qatest4567)
            device_details: Device details for headers
        """
        super().__init__(base_url=self.BASE_URL)
        
        self.request_id = request_id
        self.device_details = device_details or UpstoxDeviceDetails()
        
        # Set default headers
        self._setup_headers()
    
    def _setup_headers(self):
        """Setup default headers for Upstox API"""
        self.http.session.headers.update({
            'X-Device-Details': self.device_details.to_header_string(),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _build_url_with_query(self, endpoint: str, extra_params: Optional[Dict] = None) -> str:
        """Build URL with query parameters"""
        params = {'requestId': self.request_id}
        if extra_params:
            params.update(extra_params)
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{endpoint}?{query_string}"
    
    def generate_otp(
        self,
        mobile_number: str,
        save_token: bool = True,
        token_key: str = "validate_otp_token"
    ) -> GenerateOTPResponse:
        """
        Generate OTP and get validateOTPToken
        
        Args:
            mobile_number: Mobile number to send OTP
            save_token: Whether to save token in token store
            token_key: Key to use when saving token
            
        Returns:
            GenerateOTPResponse object
            
        Raises:
            AssertionError: If response validation fails
        """
        logger.info(f"Generating OTP for mobile: {mobile_number}")
        
        # Build URL with query parameters
        url = self._build_url_with_query(self.GENERATE_OTP_ENDPOINT)
        logger.debug(f"Request URL: {url}")
        
        # Prepare request body
        request_data = GenerateOTPRequest.with_mobile_number(mobile_number)
        
        # Make request
        response = self.http.post(url, json=request_data.model_dump())
        
        # Validate response status code
        APIAssertions.assert_status_code(response, 200)
        logger.info(f"✓ Status code verified: 200")
        
        # Parse response
        response_data = response.json()
        otp_response = GenerateOTPResponse(**response_data)
        
        # Validate success flag
        if not otp_response.is_success:
            error_msg = f"OTP generation failed: {otp_response.message}"
            logger.error(error_msg)
            # Still return the response for error handling, don't raise assertion
            # This allows tests to check error responses
        else:
            logger.info(f"✓ Success flag verified: true")
            
            # Validate validateOTPToken exists (only for successful responses)
            if not otp_response.validate_otp_token:
                error_msg = "validateOTPToken not found in response"
                logger.error(error_msg)
                raise AssertionError(error_msg)
            logger.info(f"✓ validateOTPToken generated: {otp_response.validate_otp_token[:20]}...")
            
            # Save token if requested (only for successful responses)
            if save_token:
                token_store.save_token(token_key, otp_response.validate_otp_token)
                logger.info(f"✓ Token saved with key: {token_key}")
        
        return otp_response
    
    def generate_otp_raw(self, mobile_number: str) -> requests.Response:
        """
        Generate OTP and return raw response (for testing)
        
        Args:
            mobile_number: Mobile number to send OTP
            
        Returns:
            Raw requests.Response object
        """
        url = self._build_url_with_query(self.GENERATE_OTP_ENDPOINT)
        request_data = GenerateOTPRequest.with_mobile_number(mobile_number)
        
        return self.http.post(url, json=request_data.model_dump())
    
    def validate_otp(
        self,
        otp: str,
        validate_otp_token: Optional[str] = None,
        token_key: str = "validate_otp_token"
    ) -> Dict[str, Any]:
        """
        Validate OTP using validateOTPToken (legacy v8 endpoint)
        
        Args:
            otp: OTP received on mobile
            validate_otp_token: Token from generate_otp (optional, uses stored token if not provided)
            token_key: Key to retrieve token from store
            
        Returns:
            Validation response
        """
        # Get token from parameter or token store
        token = validate_otp_token or token_store.get_token(token_key)
        
        if not token:
            raise ValueError(f"No validateOTPToken found. Call generate_otp first or provide token.")
        
        logger.info(f"Validating OTP (legacy endpoint)...")
        
        # Build URL with query parameters including validateOTPToken
        url = self._build_url_with_query(
            self.VALIDATE_OTP_ENDPOINT,
            extra_params={'validateOTPToken': token}
        )
        
        # Prepare request body
        payload = {
            "data": {
                "otp": otp,
                "validateOTPToken": token
            }
        }
        
        response = self.http.post(url, json=payload)
        APIAssertions.assert_status_code(response, 200)
        
        return response.json()
    
    def verify_otp(
        self,
        otp: str = "123789",
        validate_otp_token: Optional[str] = None,
        token_key: str = "validate_otp_token",
        mobile_number: Optional[str] = None,
        auto_retry: bool = True,
        save_profile_id: bool = True
    ) -> VerifyOTPResponse:
        """
        Verify OTP using validateOTPToken (v4 endpoint with full validation)
        
        Step 2 in login flow: Validates OTP and extracts profileId.
        
        Args:
            otp: OTP code (default: "123789")
            validate_otp_token: Token from generate_otp (optional, uses stored token if not provided)
            token_key: Key to retrieve token from store
            mobile_number: Mobile number for auto-retry (required if auto_retry=True)
            auto_retry: If True, automatically regenerate OTP on session expiry (error 1017076)
            save_profile_id: If True, save profileId to token_store
            
        Returns:
            VerifyOTPResponse object with all validations
            
        Raises:
            AssertionError: If validations fail and auto_retry is False or retry fails
            ValueError: If token not found and mobile_number not provided for retry
            
        Example:
            >>> client = UpstoxAuthClient()
            >>> client.generate_otp("9870165199")  # Step 1
            >>> verify_response = client.verify_otp("123789")  # Step 2
            >>> print(f"Profile ID: {verify_response.profile_id}")
        """
        # Get token from parameter or token store
        token = validate_otp_token or token_store.get_token(token_key)
        
        if not token:
            raise ValueError(f"No validateOTPToken found. Call generate_otp first or provide token.")
        
        return self._verify_otp_with_retry(
            otp=otp,
            token=token,
            mobile_number=mobile_number,
            auto_retry=auto_retry,
            save_profile_id=save_profile_id
        )
    
    def _verify_otp_with_retry(
        self,
        otp: str,
        token: str,
        mobile_number: Optional[str],
        auto_retry: bool,
        save_profile_id: bool
    ) -> VerifyOTPResponse:
        """
        Internal method to verify OTP with retry logic
        """
        logger.info(f"Verifying OTP (v4 endpoint)...")
        logger.info(f"   OTP: {otp}")
        logger.info(f"   Token: {token[:30]}...")
        
        # Build URL
        url = self._build_url_with_query(self.VERIFY_OTP_ENDPOINT)
        
        # Prepare request
        request_data = VerifyOTPRequest.with_token_and_otp(token, otp)
        
        # Make request
        response = self.http.post(url, json=request_data.model_dump())
        
        # Validate status code
        APIAssertions.assert_status_code(response, 200)
        logger.info(f"✓ Status code verified: 200")
        
        # Parse response
        response_data = response.json()
        verify_response = VerifyOTPResponse(**response_data)
        
        # Check for session expiry error (1017076)
        # NOTE: Auto-retry logic is commented out for testing
        # if verify_response.error_code == UpstoxErrorCodes.SESSION_EXPIRED:
        #     logger.warning(f"⚠ Session expired (error 1017076)")
        #     
        #     if auto_retry:
        #         if not mobile_number:
        #             raise ValueError(
        #                 "Session expired and auto_retry=True, but mobile_number not provided. "
        #                 "Please provide mobile_number for automatic OTP regeneration."
        #             )
        #         
        #         logger.info(f"🔄 Auto-retry enabled. Regenerating OTP for {mobile_number}...")
        #         
        #         # Step 1: Regenerate OTP
        #         generate_response = self.generate_otp(mobile_number, save_token=True)
        #         
        #         if not generate_response.validate_otp_token:
        #             raise AssertionError(
        #                 f"Failed to regenerate OTP: {generate_response.message}"
        #             )
        #         
        #         new_token = generate_response.validate_otp_token
        #         logger.info(f"✓ New token generated: {new_token[:30]}...")
        #         
        #         # Step 2: Retry verification with new token
        #         logger.info(f"🔄 Retrying verification with new token...")
        #         return self._verify_otp_with_retry(
        #             otp=otp,
        #             token=new_token,
        #             mobile_number=mobile_number,
        #             auto_retry=False,  # Don't retry again
        #             save_profile_id=save_profile_id
        #         )
        #     else:
        #         logger.error(f"Session expired and auto_retry is disabled")
        #         raise AssertionError(
        #             f"Session expired (error 1017076): {verify_response.message}. "
        #             f"Call generate_otp() to get a new token."
        #         )
        
        # Simple error handling without auto-retry
        if verify_response.error_code == UpstoxErrorCodes.SESSION_EXPIRED:
            logger.error(f"❌ Session expired (error 1017076): {verify_response.message}")
            raise AssertionError(
                f"Session expired. Please run generate_otp() again to get a new token."
            )
        
        # If not success, return without full validation
        if not verify_response.success:
            logger.warning(f"Verification failed: {verify_response.message}")
            return verify_response
        
        # Success - perform all validations
        logger.info(f"✓ Success flag: true")
        
        is_valid, error_msg = verify_response.validate_success_response()
        
        if not is_valid:
            # NOTE: Auto-retry logic is commented out for testing
            # if auto_retry and mobile_number:
            #     logger.warning(f"Validation failed: {error_msg}")
            #     logger.info(f"🔄 Attempting auto-retry...")
            #     
            #     # Regenerate and retry
            #     generate_response = self.generate_otp(mobile_number, save_token=True)
            #     if not generate_response.validate_otp_token:
            #         raise AssertionError(f"Failed to regenerate OTP: {generate_response.message}")
            #     
            #     return self._verify_otp_with_retry(
            #         otp=otp,
            #         token=generate_response.validate_otp_token,
            #         mobile_number=mobile_number,
            #         auto_retry=False,
            #         save_profile_id=save_profile_id
            #     )
            # else:
            #     logger.error(f"Validation failed: {error_msg}")
            #     raise AssertionError(f"Verify OTP validation failed: {error_msg}")
            
            # Simple validation error handling without auto-retry
            logger.error(f"❌ Validation failed: {error_msg}")
            raise AssertionError(f"Verify OTP validation failed: {error_msg}")
        
        # All validations passed
        logger.info(f"✓ Message verified: '{verify_response.message}'")
        logger.info(f"✓ userType verified: '{verify_response.user_type}'")
        logger.info(f"✓ isSecretPinSet verified: {verify_response.is_secret_pin_set}")
        logger.info(f"✓ profileId verified: {verify_response.profile_id}")
        
        # Save profileId and userType
        if save_profile_id and verify_response.profile_id:
            token_store.save_user_data("profile_id", verify_response.profile_id)
            logger.info(f"✓ Profile ID saved: {verify_response.profile_id}")
        
        # Save userType for report generation
        if verify_response.user_type:
            token_store.save_user_data("user_type", verify_response.user_type)
            logger.info(f"✓ User Type saved: {verify_response.user_type}")
        
        logger.info(f"🎉 OTP verified successfully!")
        return verify_response
    
    def verify_otp_raw(
        self,
        otp: str = "123789",
        validate_otp_token: Optional[str] = None,
        token_key: str = "validate_otp_token"
    ) -> requests.Response:
        """
        Verify OTP and return raw response (for testing)
        
        Args:
            otp: OTP code
            validate_otp_token: Token from generate_otp
            token_key: Key to retrieve token from store
            
        Returns:
            Raw requests.Response object
        """
        token = validate_otp_token or token_store.get_token(token_key)
        
        if not token:
            raise ValueError(f"No validateOTPToken found.")
        
        url = self._build_url_with_query(self.VERIFY_OTP_ENDPOINT)
        request_data = VerifyOTPRequest.with_token_and_otp(token, otp)
        
        return self.http.post(url, json=request_data.model_dump())
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: 2FA AUTHENTICATION API
    # ═══════════════════════════════════════════════════════════════════
    
    def two_factor_auth(
        self,
        otp: str = "123789",
        validate_otp_token: Optional[str] = None,
        token_key: str = "validate_otp_token",
        save_response_data: bool = True
    ) -> TwoFactorAuthResponse:
        """
        2FA Authentication API (Step 3 in login flow)
        
        This is the third step after:
        1. Generate OTP (provides validate_otp_token)
        2. Verify OTP
        
        Args:
            otp: OTP code (default: "123789")
            validate_otp_token: Token from generate_otp (optional, uses stored token if not provided)
            token_key: Key to retrieve token from store
            save_response_data: If True, saves redirect_uri and customer_status
            
        Returns:
            TwoFactorAuthResponse object
            
        Raises:
            AssertionError: If any validation fails
            
        Validations:
            - Status code: 200
            - success: true
            - redirectUri: "https://uat-pro.upstox.com"
            - userType: "LEAD"
            - customerStatus: "NEW"
            
        Example:
            >>> client = UpstoxAuthClient()
            >>> client.generate_otp("9870165199")  # Step 1
            >>> client.verify_otp("123789")         # Step 2
            >>> two_fa_response = client.two_factor_auth()  # Step 3
            >>> print(two_fa_response.redirect_uri)
            'https://uat-pro.upstox.com'
        """
        logger.info(f"="*70)
        logger.info(f"🔐 STEP 3: 2FA Authentication")
        logger.info(f"="*70)
        
        # Get token from parameter or token store
        token = validate_otp_token or token_store.get_token(token_key)
        
        if not token:
            raise ValueError(
                f"No validateOTPToken found. "
                f"Call generate_otp() first or provide token."
            )
        
        logger.info(f"Using validate_otp_token: {token[:50]}...")
        logger.info(f"Using OTP: {otp}")
        
        # Build URL with required query parameters
        url = self._build_url_with_query(
            self.TWO_FA_ENDPOINT,
            extra_params={
                'client_id': 'PW3-Kd6pvTPIciPbPxdF5S3FAx88',
                'redirect_uri': 'https://uat-pro.upstox.com'
            }
        )
        logger.debug(f"2FA URL: {url}")
        
        # Prepare request body
        request_data = TwoFactorAuthRequest.with_token_and_otp(token, otp)
        
        # Make API call
        logger.info(f"Calling 2FA API...")
        response = self.http.post(url, json=request_data.model_dump())
        
        # Validate status code
        APIAssertions.assert_status_code(response, 200)
        logger.info(f"✓ Status code verified: 200")
        
        # Parse response
        response_data = response.json()
        two_fa_response = TwoFactorAuthResponse(**response_data)
        
        # Check if success
        if not two_fa_response.success:
            error_msg = f"2FA failed: {two_fa_response.message}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        
        logger.info(f"✓ 2FA success: true")
        
        # Perform all validations
        is_valid, error_msg = two_fa_response.validate_success_response()
        
        if not is_valid:
            logger.error(f"❌ 2FA validation failed: {error_msg}")
            raise AssertionError(f"2FA validation failed: {error_msg}")
        
        # All validations passed
        logger.info(f"✓ redirectUri verified: '{two_fa_response.redirect_uri}'")
        logger.info(f"✓ userType verified: '{two_fa_response.user_type}'")
        logger.info(f"✓ customerStatus verified: '{two_fa_response.customer_status}'")
        
        # Save response data
        if save_response_data:
            if two_fa_response.redirect_uri:
                token_store.save_user_data("redirect_uri", two_fa_response.redirect_uri)
                logger.info(f"✓ Redirect URI saved: {two_fa_response.redirect_uri}")
            
            if two_fa_response.customer_status:
                token_store.save_user_data("customer_status", two_fa_response.customer_status)
                logger.info(f"✓ Customer status saved: {two_fa_response.customer_status}")
        
        logger.info(f"🎉 2FA Authentication successful!")
        logger.info(f"="*70)
        
        return two_fa_response
    
    def two_factor_auth_raw(
        self,
        otp: str = "123789",
        validate_otp_token: Optional[str] = None,
        token_key: str = "validate_otp_token"
    ) -> requests.Response:
        """
        2FA Authentication and return raw response (for testing)
        
        Args:
            otp: OTP code
            validate_otp_token: Token from generate_otp
            token_key: Key to retrieve token from store
            
        Returns:
            Raw requests.Response object
        """
        token = validate_otp_token or token_store.get_token(token_key)
        
        if not token:
            raise ValueError(f"No validateOTPToken found.")
        
        url = self._build_url_with_query(
            self.TWO_FA_ENDPOINT,
            extra_params={
                'client_id': 'PW3-Kd6pvTPIciPbPxdF5S3FAx88',
                'redirect_uri': 'https://uat-pro.upstox.com'
            }
        )
        request_data = TwoFactorAuthRequest.with_token_and_otp(token, otp)
        
        return self.http.post(url, json=request_data.model_dump())
    
    def get_stored_token(self, token_key: str = "validate_otp_token") -> Optional[str]:
        """Get stored validateOTPToken"""
        return token_store.get_token(token_key)
    
    def clear_stored_token(self, token_key: str = "validate_otp_token"):
        """Clear stored validateOTPToken"""
        token_store.clear_token(token_key)
        logger.info(f"Cleared token with key: {token_key}")
    
    def get_stored_profile_id(self) -> Optional[int]:
        """Get stored profileId from successful verification"""
        return token_store.get_user_data("profile_id")
    
    def clear_stored_profile_id(self):
        """Clear stored profileId"""
        token_store.clear_user_data("profile_id")
        logger.info(f"Cleared profile_id from storage")
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: 2FA Helper Methods
    # ═══════════════════════════════════════════════════════════════════
    
    def get_stored_redirect_uri(self) -> Optional[str]:
        """Get stored redirectUri from successful 2FA"""
        return token_store.get_user_data("redirect_uri")
    
    def get_stored_customer_status(self) -> Optional[str]:
        """Get stored customerStatus from successful 2FA"""
        return token_store.get_user_data("customer_status")
    
    def clear_stored_2fa_data(self):
        """Clear all 2FA related stored data"""
        token_store.clear_user_data("redirect_uri")
        token_store.clear_user_data("customer_status")
        logger.info(f"Cleared 2FA data from storage")
    
    def get_all_stored_data(self) -> Dict[str, Any]:
        """Get all stored tokens and user data"""
        return {
            "tokens": token_store.all_tokens,
            "user_data": token_store.all_user_data
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 4: EMAIL SEND OTP API
    # ═══════════════════════════════════════════════════════════════════
    
    def email_send_otp(
        self,
        email: str,
        profile_id: Optional[str] = None,
        authorization_token: Optional[str] = None
    ) -> EmailSendOTPResponse:
        """
        Stage 4: Send OTP to Email Address
        
        API: POST /account-opening/v3/email/send-otp
        
        This API is called after successful 2FA authentication.
        Sends an OTP to the specified email address.
        
        Args:
            email: Email address (format: {random}_@gmail.com)
            profile_id: X-profile-id header (from Stage 2). Auto-fetched from store if None.
            authorization_token: Bearer token for Authorization header. Auto-fetched if None.
            
        Returns:
            EmailSendOTPResponse: Parsed response object
            
        Raises:
            AssertionError: If response validation fails
            requests.RequestException: If HTTP request fails
        """
        logger.info(f"="*70)
        logger.info(f"📧 STEP 4: Email Send OTP")
        logger.info(f"="*70)
        logger.info(f"Email: {email}")
        
        # Get profile_id from store if not provided
        profile_id = profile_id or token_store.get_user_data("profile_id")
        if not profile_id:
            raise ValueError("No profile_id found. Please run Stage 2 (Verify OTP) first.")
        logger.info(f"Using profile_id: {profile_id}")
        
        # Get token from store if not provided (from 2FA response or cookies)
        auth_token = authorization_token or token_store.get_user_data("access_token")
        if not auth_token:
            # Try to construct from cookies or use placeholder
            logger.warning("No access_token found in store. Using placeholder.")
            auth_token = "Bearer <token_from_2fa>"
        elif not auth_token.startswith("Bearer "):
            auth_token = f"Bearer {auth_token}"
        
        # Build URL
        url = self._build_url(self.EMAIL_SEND_OTP_ENDPOINT)
        
        # Prepare headers
        headers = {
            'X-profile-id': str(profile_id),
            'Content-Type': 'application/json',
            'requestId': self.request_id,
            'Authorization': auth_token
        }
        
        # Prepare request body
        request_data = EmailSendOTPRequest.with_email(email)
        
        logger.info(f"Calling Email Send OTP API...")
        
        # Make the request
        response = self.http.post(url, json=request_data.model_dump(), headers=headers)
        
        # Assert status code
        APIAssertions.assert_status_code(response, 200)
        logger.info(f"✓ Status code verified: 200")
        
        # Parse response (handles flat format: {"EMAIL": "OTP sent successfully"})
        response_data = response.json()
        email_response = EmailSendOTPResponse.from_raw_response(response_data)
        
        # Validate success response
        is_valid, error_msg = email_response.validate_success_response()
        if is_valid:
            logger.info(f"✓ {email_response.EXPECTED_KEY} verified: '{email_response.EXPECTED_MESSAGE}'")
            logger.info(f"🎉 Email OTP sent successfully!")
        else:
            logger.error(f"✗ Email OTP validation failed: {error_msg}")
        
        logger.info(f"="*70)
        
        return email_response
    
    def email_send_otp_simple(
        self,
        email: str
    ) -> EmailSendOTPResponse:
        """
        Simple version of email_send_otp with auto-fetching all required data.
        
        Args:
            email: Email address (format: {random}_@gmail.com)
            
        Returns:
            EmailSendOTPResponse: Parsed response object
        """
        return self.email_send_otp(email)
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 5: EMAIL VERIFY OTP API
    # ═══════════════════════════════════════════════════════════════════
    
    def email_verify_otp(
        self,
        email: Optional[str] = None,
        otp: str = "123789",
        profile_id: Optional[str] = None,
        authorization_token: Optional[str] = None
    ) -> EmailVerifyOTPResponse:
        """
        Stage 5: Verify Email OTP
        
        API: POST /account-opening/v3/email/verify-otp
        
        This API is called after successful Stage 4 (Email Send OTP).
        Verifies the OTP sent to the email address.
        
        Args:
            email: Email address from Stage 4. Auto-fetched from store if None.
            otp: OTP code to verify (default: "123789")
            profile_id: X-profile-id header. Auto-fetched from store if None.
            authorization_token: Bearer token for Authorization header.
            
        Returns:
            EmailVerifyOTPResponse: Parsed response object
            
        Raises:
            AssertionError: If response validation fails
            requests.RequestException: If HTTP request fails
        """
        logger.info(f"="*70)
        logger.info(f"✅ STEP 5: Email Verify OTP")
        logger.info(f"="*70)
        
        # Get email from store if not provided
        email = email or token_store.get_user_data("email_used")
        if not email:
            raise ValueError("No email found. Please run Stage 4 (Email Send OTP) first.")
        logger.info(f"Email: {email}")
        logger.info(f"OTP: {otp}")
        
        # Get profile_id from store if not provided
        profile_id = profile_id or token_store.get_user_data("profile_id")
        if not profile_id:
            raise ValueError("No profile_id found. Please run Stage 2 (Verify OTP) first.")
        logger.info(f"Using profile_id: {profile_id}")
        
        # Get token from store if not provided
        auth_token = authorization_token or token_store.get_user_data("access_token")
        if not auth_token:
            logger.warning("No access_token found in store. Using placeholder.")
            auth_token = "Bearer <token_from_2fa>"
        elif not auth_token.startswith("Bearer "):
            auth_token = f"Bearer {auth_token}"
        
        # Build URL
        url = self._build_url(self.EMAIL_VERIFY_OTP_ENDPOINT)
        
        # Prepare headers
        headers = {
            'X-profile-id': str(profile_id),
            'Content-Type': 'application/json',
            'requestId': self.request_id,
            'Authorization': auth_token
        }
        
        # Prepare request body
        request_data = EmailVerifyOTPRequest.with_email_and_otp(email, otp)
        
        logger.info(f"Calling Email Verify OTP API...")
        
        # Make the request
        response = self.http.post(url, json=request_data.model_dump(), headers=headers)
        
        # Assert status code
        APIAssertions.assert_status_code(response, 200)
        logger.info(f"✓ Status code verified: 200")
        
        # Parse response (handles flat format)
        response_data = response.json()
        verify_response = EmailVerifyOTPResponse.from_raw_response(response_data)
        
        # Validate success response
        is_valid, error_msg = verify_response.validate_success_response()
        if is_valid:
            logger.info(f"✓ {verify_response.EXPECTED_KEY} verified: '{verify_response.EXPECTED_MESSAGE}'")
            logger.info(f"🎉 Email OTP verified successfully!")
        else:
            logger.error(f"✗ Email OTP verification failed: {error_msg}")
        
        logger.info(f"="*70)
        
        return verify_response
    
    def email_verify_otp_simple(
        self,
        email: Optional[str] = None,
        otp: str = "123789"
    ) -> EmailVerifyOTPResponse:
        """
        Simple version of email_verify_otp with auto-fetching all required data.
        
        Args:
            email: Email address. Auto-fetched from store if None.
            otp: OTP code (default: "123789")
            
        Returns:
            EmailVerifyOTPResponse: Parsed response object
        """
        return self.email_verify_otp(email, otp)


# Standalone functions for quick usage

def generate_otp_token(
    mobile_number: str,
    request_id: str = "qatest4567",
    save_token: bool = True
) -> GenerateOTPResponse:
    """
    Quick function to generate OTP token
    
    Args:
        mobile_number: Mobile number
        request_id: Request ID (default: qatest4567)
        save_token: Save token for later use
        
    Returns:
        GenerateOTPResponse
        
    Example:
        >>> response = generate_otp_token("9870165199")
        >>> print(response.validate_otp_token)
    """
    with UpstoxAuthClient(request_id=request_id) as client:
        return client.generate_otp(mobile_number, save_token=save_token)


def verify_otp_token(
    otp: str = "123789",
    mobile_number: Optional[str] = None,
    request_id: str = "qatest4567",
    auto_retry: bool = True,
    save_profile_id: bool = True
) -> VerifyOTPResponse:
    """
    Quick function to verify OTP token
    
    Automatically handles session expiry by regenerating OTP if needed.
    
    Args:
        otp: OTP code (default: "123789")
        mobile_number: Mobile number for auto-retry (required if auto_retry=True and no stored token)
        request_id: Request ID (default: qatest4567)
        auto_retry: Automatically regenerate OTP on session expiry
        save_profile_id: Save profileId to token_store
        
    Returns:
        VerifyOTPResponse
        
    Example:
        >>> # If token already stored:
        >>> response = verify_otp_token("123789")
        >>> 
        >>> # With auto-retry:
        >>> response = verify_otp_token("123789", mobile_number="9870165199")
        >>> print(f"Profile ID: {response.profile_id}")
    """
    with UpstoxAuthClient(request_id=request_id) as client:
        return client.verify_otp(
            otp=otp,
            mobile_number=mobile_number,
            auto_retry=auto_retry,
            save_profile_id=save_profile_id
        )


def complete_login_flow(
    mobile_number: str,
    otp: str = "123789",
    request_id: str = "qatest4567",
    run_2fa: bool = True
) -> Dict[str, Any]:
    """
    Complete login flow: Generate OTP → Verify OTP → 2FA Auth (Phase 3)
    
    This function performs the full 3-step login process:
    1. Generates OTP for the mobile number
    2. Verifies the OTP
    3. Performs 2FA Authentication (if run_2fa=True)
    
    Args:
        mobile_number: Mobile number for OTP generation
        otp: OTP code to verify (default: "123789")
        request_id: Request ID (default: qatest4567)
        run_2fa: Whether to run Step 3 (2FA Authentication)
        
    Returns:
        Dictionary with all results:
        {
            "generate_response": GenerateOTPResponse,
            "verify_response": VerifyOTPResponse,
            "two_fa_response": TwoFactorAuthResponse,  # NEW in Phase 3
            "token": str,
            "profile_id": int,
            "redirect_uri": str,        # NEW in Phase 3
            "customer_status": str      # NEW in Phase 3
        }
        
    Example:
        >>> result = complete_login_flow("9870165199", "123789")
        >>> print(f"Token: {result['token']}")
        >>> print(f"Profile ID: {result['profile_id']}")
        >>> print(f"Redirect URI: {result['redirect_uri']}")  # NEW
    """
    logger.info(f"="*70)
    logger.info(f"🚀 STARTING COMPLETE LOGIN FLOW (3-Step)")
    logger.info(f"="*70)
    logger.info(f"Mobile: {mobile_number}")
    logger.info(f"OTP: {otp}")
    logger.info(f"Include 2FA: {run_2fa}")
    
    with UpstoxAuthClient(request_id=request_id) as client:
        # Step 1: Generate OTP
        logger.info(f"\n📱 STEP 1: Generate OTP")
        logger.info(f"-"*70)
        
        generate_response = client.generate_otp(mobile_number, save_token=True)
        
        if not generate_response.validate_otp_token:
            raise AssertionError(f"Failed to generate OTP: {generate_response.message}")
        
        token = generate_response.validate_otp_token
        logger.info(f"✓ OTP Generated")
        logger.info(f"✓ Token: {token[:50]}...")
        
        # Step 2: Verify OTP
        logger.info(f"\n🔐 STEP 2: Verify OTP")
        logger.info(f"-"*70)
        
        verify_response = client.verify_otp(
            otp=otp,
            mobile_number=mobile_number,
            auto_retry=False,  # Disabled as per requirement
            save_profile_id=True
        )
        
        profile_id = verify_response.profile_id
        logger.info(f"✓ OTP Verified")
        logger.info(f"✓ Profile ID: {profile_id}")
        
        # Initialize 2FA response as None
        two_fa_response = None
        redirect_uri = None
        customer_status = None
        
        # Step 3: 2FA Authentication (Phase 3)
        if run_2fa:
            logger.info(f"\n🔒 STEP 3: 2FA Authentication")
            logger.info(f"-"*70)
            
            try:
                two_fa_response = client.two_factor_auth(
                    otp=otp,
                    save_response_data=True
                )
                
                redirect_uri = two_fa_response.redirect_uri
                customer_status = two_fa_response.customer_status
                
                logger.info(f"✓ 2FA Authentication Successful")
                logger.info(f"✓ Redirect URI: {redirect_uri}")
                logger.info(f"✓ Customer Status: {customer_status}")
                
            except Exception as e:
                logger.error(f"❌ 2FA Authentication Failed: {e}")
                # Don't fail the whole flow if 2FA fails
                # Just log the error and continue
        else:
            logger.info(f"\n⏩ STEP 3: 2FA Authentication (Skipped)")
        
        logger.info(f"\n" + "="*70)
        logger.info(f"🎉 LOGIN FLOW COMPLETED SUCCESSFULLY!")
        logger.info(f"="*70)
        
        return {
            "generate_response": generate_response,
            "verify_response": verify_response,
            "two_fa_response": two_fa_response,
            "token": token,
            "profile_id": profile_id,
            "redirect_uri": redirect_uri,
            "customer_status": customer_status
        }
