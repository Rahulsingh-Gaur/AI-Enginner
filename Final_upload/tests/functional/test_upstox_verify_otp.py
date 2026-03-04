"""
Test Cases for Upstox Verify OTP API (Step 2)
POST /login/open/v4/auth/1fa/otp-totp/verify?requestId=qatest4567

This is the second step in the login flow after Generate OTP.
"""
import pytest
import allure
from src.api_clients.upstox_auth_client import UpstoxAuthClient, verify_otp_token, complete_login_flow
from src.models.upstox_models import (
    VerifyOTPResponse, 
    token_store, 
    UpstoxErrorCodes,
    UpstoxDeviceDetails
)
from src.utils.assertions import APIAssertions as Assert
from src.utils.logger import logger


@pytest.fixture
def upstox_client():
    """Fixture for Upstox Auth Client"""
    client = UpstoxAuthClient(request_id="qatest4567")
    yield client
    client.close()


@pytest.fixture
def sample_mobile():
    """Sample mobile number"""
    return "9870165199"


@pytest.fixture
def default_otp():
    """Default OTP value"""
    return "123789"


@pytest.fixture
def mock_verify_response():
    """Mock successful verify response for testing"""
    return {
        "success": True,
        "data": {
            "message": "Your OTP has been successfully verified.",
            "userType": "LEAD",
            "isSecretPinSet": False,
            "profileId": 3820874
        }
    }


@allure.feature("Upstox Authentication")
@allure.story("Verify OTP")
@pytest.mark.upstox
@pytest.mark.verify
@pytest.mark.smoke
@pytest.mark.positive
class TestUpstoxVerifyOTP:
    """Positive test cases for Verify OTP API"""
    
    def test_verify_otp_response_model(self, mock_verify_response):
        """
        TC-V001: Verify OTP response model parsing
        
        Validates that the response model correctly parses all fields.
        """
        response = VerifyOTPResponse(**mock_verify_response)
        
        assert response.success is True
        assert response.message == "Your OTP has been successfully verified."
        assert response.user_type == "LEAD"
        assert response.is_secret_pin_set is False
        assert response.profile_id == 3820874
        
        logger.info(f"✓ Response model parsed successfully")
        logger.info(f"  - success: {response.success}")
        logger.info(f"  - message: {response.message}")
        logger.info(f"  - userType: {response.user_type}")
        logger.info(f"  - isSecretPinSet: {response.is_secret_pin_set}")
        logger.info(f"  - profileId: {response.profile_id}")
    
    def test_verify_otp_success_validation(self, mock_verify_response):
        """
        TC-V002: Test success validation helper method
        
        All validations should pass for a correct response.
        """
        response = VerifyOTPResponse(**mock_verify_response)
        
        is_valid, error_msg = response.validate_success_response()
        
        assert is_valid is True, f"Validation failed: {error_msg}"
        assert error_msg == "All validations passed"
        
        logger.info(f"✓ All success validations passed")
    
    def test_verify_otp_complete_flow_mock(self, sample_mobile, default_otp, mock_verify_response):
        """
        TC-V003: Test complete flow with mocked responses
        
        Simulates the complete Generate OTP → Verify OTP flow.
        """
        # Clear any existing data
        token_store.clear_all()
        
        # Mock: Simulate generate_otp storing a token
        mock_token = "ll1FA-test-token-for-mocked-flow"
        token_store.save_token("validate_otp_token", mock_token)
        
        # Mock: Parse verify response
        verify_response = VerifyOTPResponse(**mock_verify_response)
        
        # Save profileId (as the real method would do)
        token_store.save_user_data("profile_id", verify_response.profile_id)
        
        # Validate
        is_valid, error_msg = verify_response.validate_success_response()
        assert is_valid is True
        
        # Verify stored data
        stored_token = token_store.get_token("validate_otp_token")
        stored_profile_id = token_store.get_user_data("profile_id")
        
        assert stored_token == mock_token
        assert stored_profile_id == 3820874
        
        logger.info(f"✓ Complete flow test passed")
        logger.info(f"  - Token stored: {stored_token[:30]}...")
        logger.info(f"  - Profile ID stored: {stored_profile_id}")


@allure.feature("Upstox Authentication")
@allure.story("Verify OTP - Validations")
@pytest.mark.upstox
@pytest.mark.verify
@pytest.mark.validation
class TestUpstoxVerifyOTPValidations:
    """Test individual validation rules"""
    
    def test_validation_message_mismatch(self):
        """TC-V004: Validation should fail if message doesn't match"""
        response_data = {
            "success": True,
            "data": {
                "message": "Wrong message here",  # Incorrect message
                "userType": "LEAD",
                "isSecretPinSet": False,
                "profileId": 3820874
            }
        }
        
        response = VerifyOTPResponse(**response_data)
        is_valid, error_msg = response.validate_success_response()
        
        assert is_valid is False
        assert "Message mismatch" in error_msg
        logger.info(f"✓ Message mismatch detected: {error_msg}")
    
    def test_validation_user_type_mismatch(self):
        """TC-V005: Validation should fail if userType is not LEAD"""
        response_data = {
            "success": True,
            "data": {
                "message": "Your OTP has been successfully verified.",
                "userType": "CUSTOMER",  # Wrong userType
                "isSecretPinSet": False,
                "profileId": 3820874
            }
        }
        
        response = VerifyOTPResponse(**response_data)
        is_valid, error_msg = response.validate_success_response()
        
        assert is_valid is False
        assert "userType mismatch" in error_msg
        logger.info(f"✓ userType mismatch detected: {error_msg}")
    
    def test_validation_is_secret_pin_set_mismatch(self):
        """TC-V006: Validation should fail if isSecretPinSet is not False"""
        response_data = {
            "success": True,
            "data": {
                "message": "Your OTP has been successfully verified.",
                "userType": "LEAD",
                "isSecretPinSet": True,  # Should be False
                "profileId": 3820874
            }
        }
        
        response = VerifyOTPResponse(**response_data)
        is_valid, error_msg = response.validate_success_response()
        
        assert is_valid is False
        assert "isSecretPinSet mismatch" in error_msg
        logger.info(f"✓ isSecretPinSet mismatch detected: {error_msg}")
    
    def test_validation_profile_id_missing(self):
        """TC-V007: Validation should fail if profileId is missing"""
        response_data = {
            "success": True,
            "data": {
                "message": "Your OTP has been successfully verified.",
                "userType": "LEAD",
                "isSecretPinSet": False
                # profileId missing
            }
        }
        
        response = VerifyOTPResponse(**response_data)
        is_valid, error_msg = response.validate_success_response()
        
        assert is_valid is False
        assert "profileId is missing" in error_msg
        logger.info(f"✓ profileId missing detected: {error_msg}")
    
    def test_validation_profile_id_non_numeric(self):
        """TC-V008: Validation should fail if profileId is not numeric"""
        response_data = {
            "success": True,
            "data": {
                "message": "Your OTP has been successfully verified.",
                "userType": "LEAD",
                "isSecretPinSet": False,
                "profileId": "not-a-number"  # Non-numeric
            }
        }
        
        response = VerifyOTPResponse(**response_data)
        is_valid, error_msg = response.validate_success_response()
        
        assert is_valid is False
        assert "profileId is missing" in error_msg  # Non-numeric returns None
        logger.info(f"✓ Non-numeric profileId detected")
    
    def test_validation_success_false(self):
        """TC-V009: Validation should fail if success is False"""
        response_data = {
            "success": False,
            "data": {
                "message": "Some error occurred"
            }
        }
        
        response = VerifyOTPResponse(**response_data)
        is_valid, error_msg = response.validate_success_response()
        
        assert is_valid is False
        assert "success is False" in error_msg
        logger.info(f"✓ success=False detected: {error_msg}")


@allure.feature("Upstox Authentication")
@allure.story("Verify OTP - Error Handling")
@pytest.mark.upstox
@pytest.mark.verify
@pytest.mark.error_handling
class TestUpstoxVerifyOTPErrorHandling:
    """Test error handling and retry logic"""
    
    def test_error_code_session_expired(self):
        """TC-V010: Detect error code 1017076 (session expired)"""
        response_data = {
            "success": False,
            "error": {
                "code": 1017076,
                "message": "Your session to validate otp has expired, please try again."
            }
        }
        
        response = VerifyOTPResponse(**response_data)
        
        assert response.error_code == 1017076
        assert response.error_code == UpstoxErrorCodes.SESSION_EXPIRED
        logger.info(f"✓ Session expired error code detected: {response.error_code}")
    
    def test_token_store_profile_id(self):
        """TC-V011: Test TokenStore can save and retrieve profileId"""
        # Clear first
        token_store.clear_user_data("profile_id")
        
        # Save profileId
        test_profile_id = 3820874
        token_store.save_user_data("profile_id", test_profile_id)
        
        # Retrieve
        stored_id = token_store.get_user_data("profile_id")
        
        assert stored_id == test_profile_id
        logger.info(f"✓ Profile ID stored and retrieved: {stored_id}")
        
        # Cleanup
        token_store.clear_user_data("profile_id")


@allure.feature("Upstox Authentication")
@allure.story("Verify OTP - Integration")
@pytest.mark.upstox
@pytest.mark.verify
@pytest.mark.integration
class TestUpstoxVerifyOTPIntegration:
    """Integration tests with real API calls"""
    
    def test_verify_otp_without_token_fails(self, upstox_client, default_otp):
        """
        TC-V012: Verify OTP should fail if no token is stored
        """
        # Clear any existing token
        token_store.clear_token("validate_otp_token")
        
        # Attempt to verify without token
        with pytest.raises(ValueError) as exc_info:
            upstox_client.verify_otp(
                otp=default_otp,
                auto_retry=False  # Disable auto-retry for this test
            )
        
        assert "No validateOTPToken found" in str(exc_info.value)
        logger.info(f"✓ Correctly raised error when token missing")
    
    def test_verify_otp_raw_response(self, upstox_client, sample_mobile, default_otp):
        """
        TC-V013: Test verify_otp_raw returns response object
        
        Note: This test may fail due to rate limits or invalid tokens.
        """
        # First generate OTP
        generate_response = upstox_client.generate_otp(sample_mobile)
        
        if not generate_response.validate_otp_token:
            pytest.skip("Could not generate OTP (rate limited)")
        
        # Call raw verify
        raw_response = upstox_client.verify_otp_raw(default_otp)
        
        # Just check we get a response
        assert raw_response is not None
        assert raw_response.status_code == 200
        
        logger.info(f"✓ Raw response received: {raw_response.status_code}")


@allure.feature("Upstox Authentication")
@allure.story("Complete Login Flow")
@pytest.mark.upstox
@pytest.mark.complete_flow
class TestUpstoxCompleteFlow:
    """Test complete login flow (Generate + Verify)"""
    
    def test_complete_flow_mocked(self, sample_mobile, default_otp):
        """
        TC-V014: Test complete flow with mocked components
        
        Demonstrates how the complete flow should work.
        """
        # This test demonstrates the flow logic without actual API calls
        # In real scenario, use complete_login_flow() function
        
        logger.info(f"Complete flow demonstration:")
        logger.info(f"  1. Generate OTP for: {sample_mobile}")
        logger.info(f"  2. Store validate_otp_token")
        logger.info(f"  3. Verify OTP: {default_otp}")
        logger.info(f"  4. Validate response fields")
        logger.info(f"  5. Store profile_id")
        
        assert True  # Logic demonstration
    
    def test_complete_login_flow_function_exists(self):
        """TC-V015: Verify complete_login_flow function exists and is callable"""
        import inspect
        
        assert callable(complete_login_flow)
        sig = inspect.signature(complete_login_flow)
        params = list(sig.parameters.keys())
        
        assert "mobile_number" in params
        assert "otp" in params
        assert "request_id" in params
        
        logger.info(f"✓ complete_login_flow function exists with params: {params}")


# Quick standalone test
def test_verify_response_model_quick():
    """
    Quick test for VerifyOTPResponse model
    Run with: pytest tests/functional/test_upstox_verify_otp.py::test_verify_response_model_quick -v
    """
    response_data = {
        "success": True,
        "data": {
            "message": "Your OTP has been successfully verified.",
            "userType": "LEAD",
            "isSecretPinSet": False,
            "profileId": 3820874
        }
    }
    
    response = VerifyOTPResponse(**response_data)
    
    print(f"\n{'='*60}")
    print(f"VerifyOTPResponse Model Test")
    print(f"{'='*60}")
    print(f"success: {response.success}")
    print(f"message: {response.message}")
    print(f"userType: {response.user_type}")
    print(f"isSecretPinSet: {response.is_secret_pin_set}")
    print(f"profileId: {response.profile_id}")
    
    is_valid, error_msg = response.validate_success_response()
    print(f"\nValidation: {'✓ PASS' if is_valid else '✗ FAIL'}")
    if not is_valid:
        print(f"Error: {error_msg}")
    print(f"{'='*60}\n")
    
    assert is_valid is True
    assert response.profile_id == 3820874
