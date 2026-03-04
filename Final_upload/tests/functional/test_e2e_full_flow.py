"""
E2E Test: Full 5-Stage Authentication Flow
==========================================
This test runs the complete end-to-end flow:
Stage 1: Generate OTP → Stage 2: Verify OTP → Stage 3: 2FA → Stage 4: Email OTP → Stage 5: Verify Email

Usage:
    pytest tests/functional/test_e2e_full_flow.py -v
    pytest tests/functional/test_e2e_full_flow.py -v --alluredir=reports/allure-results
"""
import pytest
import allure
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from src.api_clients.upstox_auth_client import UpstoxAuthClient
from src.models.upstox_models import token_store
from src.utils.mobile_generator import generate_unique_mobile
from src.utils.email_generator import generate_random_email


def attach_test_summary(mobile, email, profile_id, user_type, customer_status, redirect_uri=None):
    """Attach test summary to Allure report"""
    # Text summary
    summary_text = f"""
🎯 TEST DATA SUMMARY
==================================================

📱 Mobile Number:     {mobile}
📧 Email:             {email}
🆔 Profile ID:        {profile_id}
👤 User Type:         {user_type}
📊 Customer Status:   {customer_status}
🔗 Redirect URI:      {redirect_uri or 'N/A'}

==================================================
"""
    allure.attach(summary_text, name="📊 Test Summary", attachment_type=allure.attachment_type.TEXT)
    
    # JSON summary
    summary_json = {
        "mobile_number": mobile,
        "email": email,
        "profile_id": profile_id,
        "user_type": user_type,
        "customer_status": customer_status,
        "redirect_uri": redirect_uri
    }
    allure.attach(
        json.dumps(summary_json, indent=2),
        name="Test Data (JSON)",
        attachment_type=allure.attachment_type.JSON
    )


@allure.feature("E2E Flow")
@allure.story("5-Stage Authentication Flow")
@allure.severity(allure.severity_level.CRITICAL)
class TestE2EFullFlow:
    """End-to-End test for complete authentication flow"""
    
    @pytest.fixture(autouse=True)
    def setup_test(self):
        """Setup test data"""
        self.mobile_number = generate_unique_mobile()
        self.email = generate_random_email()
        self.otp = "123789"
        self.client = None
        token_store.clear_all()
        yield
        # Cleanup
        if self.client:
            self.client.close()
            
    @allure.title("E2E: Complete 5-Stage Authentication Flow")
    @allure.description("Test complete flow: Generate OTP → Verify OTP → 2FA → Email OTP → Verify Email")
    def test_e2e_full_flow(self):
        """Test complete 5-stage authentication flow"""
        
        # Attach initial test data
        allure.attach(
            f"Mobile: {self.mobile_number}\nEmail: {self.email}\nOTP: {self.otp}",
            name="📝 Initial Test Data",
            attachment_type=allure.attachment_type.TEXT
        )
        
        self.client = UpstoxAuthClient()  # Uses dynamic request ID: QATestDDMMYYHHMM
        
        # Stage 1: Generate OTP
        with allure.step("📌 Stage 1: Generate OTP"):
            response = self.client.generate_otp(self.mobile_number, save_token=True)
            allure.attach(
                f"Success: {response.success}\nMessage: {response.message}",
                name="Stage 1 Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert response.success, f"Stage 1 Failed: {response.message}"
            
        # Stage 2: Verify OTP
        with allure.step("📌 Stage 2: Verify OTP"):
            response = self.client.verify_otp(
                otp=self.otp,
                mobile_number=self.mobile_number,
                save_profile_id=True
            )
            is_valid, error_msg = response.validate_success_response()
            allure.attach(
                f"Valid: {is_valid}\nUser Type: {response.user_type}\nProfile ID: {response.profile_id}",
                name="Stage 2 Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert is_valid, f"Stage 2 Failed: {error_msg}"
            
        # Stage 3: 2FA Authentication
        with allure.step("📌 Stage 3: 2FA Authentication"):
            response = self.client.two_factor_auth(otp=self.otp)
            is_valid, error_msg = response.validate_success_response()
            allure.attach(
                f"Valid: {is_valid}\nCustomer Status: {response.customer_status}",
                name="Stage 3 Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert is_valid, f"Stage 3 Failed: {error_msg}"
            
        # Stage 4: Email Send OTP
        with allure.step("📌 Stage 4: Email Send OTP"):
            response = self.client.email_send_otp(email=self.email)
            is_valid, error_msg = response.validate_success_response()
            allure.attach(
                f"Valid: {is_valid}\nEmail: {self.email}",
                name="Stage 4 Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert is_valid, f"Stage 4 Failed: {error_msg}"
            
        # Stage 5: Email Verify OTP
        with allure.step("📌 Stage 5: Email Verify OTP"):
            response = self.client.email_verify_otp(email=self.email, otp=self.otp)
            is_valid, error_msg = response.validate_success_response()
            allure.attach(
                f"Valid: {is_valid}\nEmail Verified: {self.email}",
                name="Stage 5 Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert is_valid, f"Stage 5 Failed: {error_msg}"
            
        # Collect final data
        all_data = self.client.get_all_stored_data()
        user_data = all_data.get('user_data', {})
        
        final_summary = {
            "mobile_number": self.mobile_number,
            "email": self.email,
            "profile_id": user_data.get("profile_id"),
            "user_type": user_data.get("user_type"),
            "customer_status": user_data.get("customer_status"),
            "redirect_uri": user_data.get("redirect_uri")
        }
        
        # Attach final summary to Allure
        attach_test_summary(
            mobile=self.mobile_number,
            email=self.email,
            profile_id=user_data.get("profile_id"),
            user_type=user_data.get("user_type"),
            customer_status=user_data.get("customer_status"),
            redirect_uri=user_data.get("redirect_uri")
        )
        
        print(f"\n✅ E2E Flow Complete! Profile ID: {user_data.get('profile_id')}")


@allure.feature("E2E Flow")
@allure.story("5-Stage Flow - Auto Mode")
class TestE2EFullFlowAuto:
    """E2E test with auto-generated data (no user input)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Auto setup"""
        self.mobile = generate_unique_mobile()
        self.email = generate_random_email()
        self.otp = "123789"
        token_store.clear_all()
        yield
        
    @allure.title("E2E: Auto-Generated Data Flow")
    def test_e2e_auto_flow(self):
        """Run E2E flow with auto-generated data"""
        
        allure.attach(f"Mobile: {self.mobile}\nEmail: {self.email}", name="📝 Generated Data")
        
        client = UpstoxAuthClient()  # Uses dynamic request ID: QATestDDMMYYHHMM
        
        profile_id = None
        user_type = None
        customer_status = None
        redirect_uri = None
        
        try:
            # All stages in sequence
            with allure.step("📌 1. Generate OTP"):
                r1 = client.generate_otp(self.mobile, save_token=True)
                assert r1.success, "Generate OTP failed"
                
            with allure.step("📌 2. Verify OTP"):
                r2 = client.verify_otp(self.otp, self.mobile, save_profile_id=True)
                valid, _ = r2.validate_success_response()
                assert valid, "Verify OTP failed"
                profile_id = r2.profile_id
                user_type = r2.user_type
                
            with allure.step("📌 3. 2FA"):
                r3 = client.two_factor_auth(self.otp)
                valid, _ = r3.validate_success_response()
                assert valid, "2FA failed"
                customer_status = r3.customer_status
                redirect_uri = r3.redirect_uri
                
            with allure.step("📌 4. Email Send OTP"):
                r4 = client.email_send_otp(self.email)
                valid, _ = r4.validate_success_response()
                assert valid, "Email send failed"
                
            with allure.step("📌 5. Email Verify OTP"):
                r5 = client.email_verify_otp(self.email, self.otp)
                valid, _ = r5.validate_success_response()
                assert valid, "Email verify failed"
                
            # Attach final summary
            attach_test_summary(
                mobile=self.mobile,
                email=self.email,
                profile_id=profile_id,
                user_type=user_type,
                customer_status=customer_status,
                redirect_uri=redirect_uri
            )
            
            allure.attach("✅ All 5 stages passed!", name="Result")
            
        finally:
            client.close()
