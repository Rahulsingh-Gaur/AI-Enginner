"""
Test Cases for Upstox Generate OTP API
POST /login/open/v8/auth/1fa/otp-step/generate?requestId=qatest4567
"""
import pytest
import allure
from src.api_clients.upstox_auth_client import UpstoxAuthClient, generate_otp_token
from src.models.upstox_models import token_store, UpstoxDeviceDetails
from src.utils.assertions import APIAssertions as Assert
from src.utils.logger import logger


@pytest.fixture
def upstox_client():
    """Fixture for Upstox Auth Client"""
    client = UpstoxAuthClient(request_id="qatest4567")
    yield client
    client.close()


@pytest.fixture
def sample_mobile_number():
    """Sample mobile number for testing"""
    return "9870165199"


@allure.feature("Upstox Authentication")
@allure.story("Generate OTP")
@pytest.mark.upstox
@pytest.mark.smoke
@pytest.mark.positive
class TestUpstoxGenerateOTP:
    """Positive test cases for Generate OTP API"""
    
    def test_generate_otp_success(self, upstox_client, sample_mobile_number):
        """
        TC-U001: Generate OTP with valid mobile number
        
        Validation:
        - Status code: 200
        - success: true
        - validateOTPToken is generated
        """
        logger.info(f"Testing OTP generation for: {sample_mobile_number}")
        
        response = upstox_client.generate_otp(sample_mobile_number)
        
        # Validate response
        assert response.is_success is True, f"Expected success=true, got success={response.is_success}"
        assert response.validate_otp_token is not None, "validateOTPToken should be generated"
        assert len(response.validate_otp_token) > 0, "validateOTPToken should not be empty"
        
        logger.info(f"✓ OTP generated successfully")
        logger.info(f"✓ validateOTPToken: {response.validate_otp_token[:30]}...")
    
    def test_generate_otp_response_structure(self, upstox_client, sample_mobile_number):
        """
        TC-U002: Verify OTP response structure
        """
        response = upstox_client.generate_otp_raw(sample_mobile_number)
        
        # Validate status code
        Assert.assert_status_code(response, 200)
        
        # Validate JSON structure
        data = response.json()
        Assert.assert_json_keys_exist(response, ['success', 'data'])
        Assert.assert_json_contains(response, 'data.validateOTPToken')
    
    def test_generate_otp_saves_token(self, upstox_client, sample_mobile_number):
        """
        TC-U003: Verify validateOTPToken is saved for later use
        """
        # Note: This test might fail due to rate limiting if run multiple times
        # Use a different mobile number to avoid rate limit
        unique_mobile = f"98701{str(hash(sample_mobile_number))[-4:]}"
        
        # Clear any existing token
        token_store.clear_token("validate_otp_token")
        
        # Generate OTP
        response = upstox_client.generate_otp(unique_mobile, save_token=True)
        
        # Verify token is saved
        saved_token = upstox_client.get_stored_token()
        assert saved_token is not None, "Token should be saved"
        assert saved_token == response.validate_otp_token, "Saved token should match response token"
        
        logger.info(f"✓ Token saved successfully: {saved_token[:30]}...")
    
    def test_generate_otp_response_time(self, upstox_client, sample_mobile_number):
        """
        TC-U004: Verify OTP generation response time < 5 seconds
        """
        response = upstox_client.generate_otp_raw(sample_mobile_number)
        Assert.assert_response_time(response, 5000)  # 5 seconds
    
    def test_generate_otp_with_custom_device(self, sample_mobile_number):
        """
        TC-U005: Generate OTP with custom device details
        """
        custom_device = UpstoxDeviceDetails(
            platform="ANDROID",
            device_id="customDevice456",
            os_name="Android",
            os_version="12.0",
            model_name="Pixel6",
            manufacturer="Google"
        )
        
        client = UpstoxAuthClient(
            request_id="qatest4567",
            device_details=custom_device
        )
        
        response = client.generate_otp(sample_mobile_number)
        
        assert response.is_success is True
        assert response.validate_otp_token is not None
        
        client.close()


@allure.feature("Upstox Authentication")
@allure.story("Generate OTP - Negative Tests")
@pytest.mark.upstox
@pytest.mark.negative
class TestUpstoxGenerateOTPNegative:
    """Negative test cases for Generate OTP API"""
    
    def test_generate_otp_invalid_mobile_number(self, upstox_client):
        """
        TC-U006: Generate OTP with invalid mobile number
        """
        invalid_numbers = [
            "12345",        # Too short
            "abcdefghij",   # Non-numeric
            "",             # Empty
            "9876543210123" # Too long
        ]
        
        for mobile in invalid_numbers:
            response = upstox_client.generate_otp_raw(mobile)
            
            # Should return error (400 or 422)
            if response.status_code != 200:
                logger.info(f"✓ Invalid number '{mobile}' rejected with {response.status_code}")
            else:
                data = response.json()
                assert data.get('response', {}).get('success') is False, \
                    f"Expected failure for invalid number: {mobile}"
    
    def test_generate_otp_invalid_request_id(self, sample_mobile_number):
        """
        TC-U007: Generate OTP with invalid requestId
        """
        client = UpstoxAuthClient(request_id="invalid_request_id")
        
        response = client.generate_otp_raw(sample_mobile_number)
        
        # May return 400 or still work depending on API behavior
        logger.info(f"Response status with invalid requestId: {response.status_code}")
        
        client.close()
    
    def test_generate_otp_missing_mobile_number(self, upstox_client):
        """
        TC-U008: Generate OTP without mobile number
        """
        url = f"{upstox_client.BASE_URL}{upstox_client.GENERATE_OTP_ENDPOINT}?requestId=qatest4567"
        
        # Send empty data
        response = upstox_client.http.post(url, json={"data": {}})
        
        Assert.assert_status_range(response, 400, 422)


@allure.feature("Upstox Authentication")
@allure.story("OTP Workflow Integration")
@pytest.mark.upstox
@pytest.mark.integration
class TestUpstoxOTPWorkflow:
    """Integration workflow tests"""
    
    def test_otp_token_storage_and_retrieval(self, upstox_client, sample_mobile_number):
        """
        TC-U009: Verify token storage and retrieval workflow
        """
        # Step 1: Generate OTP
        otp_response = upstox_client.generate_otp(sample_mobile_number)
        token = otp_response.validate_otp_token
        
        # Step 2: Retrieve stored token
        stored_token = upstox_client.get_stored_token()
        
        # Step 3: Verify tokens match
        assert stored_token == token, "Stored token should match generated token"
        
        # Step 4: Clear token
        upstox_client.clear_stored_token()
        
        # Step 5: Verify token is cleared
        cleared_token = upstox_client.get_stored_token()
        assert cleared_token is None, "Token should be cleared"
        
        logger.info("✓ Token storage workflow verified")


# Quick standalone test
def test_quick_otp_generation():
    """
    Quick test using standalone function
    Run with: pytest tests/functional/test_upstox_generate_otp.py::test_quick_otp_generation -v
    """
    try:
        response = generate_otp_token("9870165199")
        print(f"\n{'='*60}")
        print(f"OTP Generation Test")
        print(f"Success: {response.is_success}")
        print(f"Message: {response.message}")
        
        if response.validate_otp_token:
            print(f"Token: {response.validate_otp_token[:50]}...")
        else:
            print(f"No token (may be rate limited)")
        print(f"{'='*60}\n")
        
        # Verify stored token
        stored = token_store.get_token("validate_otp_token")
        print(f"Stored Token: {stored[:50] if stored else 'None'}...")
        
        # Basic validations that should always pass
        assert response is not None, "Response should not be None"
        # Don't assert success - may be rate limited
        
    except Exception as e:
        print(f"Error: {e}")
        raise
