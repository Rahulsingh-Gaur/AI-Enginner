#!/usr/bin/env python3
"""
Test Runner - Main orchestrator for 5-stage flow
Extracted from auto_run_full_flow.py for better modularity
"""
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, 'src')

from src.api_clients.upstox_auth_client import UpstoxAuthClient
from src.models.upstox_models import token_store
from src.utils.mobile_generator import generate_unique_mobile
from src.utils.email_generator import generate_random_email
from .allure_helper import AllureHelper
from .stages import StageManager, StageResult


logger = logging.getLogger(__name__)


class AutoTestRunner:
    """Automatically runs all 5 stages with user input for mobile number"""

    def __init__(self, allure_enabled: bool = False, allure_results_dir: str = "reports/allure-results"):
        self.report_data = {
            "test_execution": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "timestamp": datetime.now().isoformat(),
                "environment": "UAT",
                "base_url": "https://service-uat.upstox.com"
            },
            "test_data": {},
            "api_results": [],
            "summary": {}
        }
        self.mobile_number: Optional[str] = None
        self.email: Optional[str] = None
        self.otp = "123789"
        self.client: Optional[UpstoxAuthClient] = None
        self.allure_enabled = allure_enabled
        self.allure_helper: Optional[AllureHelper] = None
        self.stage_manager: Optional[StageManager] = None
        
        if allure_enabled:
            self.allure_helper = AllureHelper(allure_results_dir)

    def allure_step(self, name: str, status: str = "passed", details: dict = None):
        """Record step for Allure report"""
        if self.allure_helper:
            self.allure_helper.add_step(name, status, details)

    def get_mobile_number_from_user(self) -> str:
        """
        Ask user to choose mobile number input method:
        1. Enter mobile number manually
        2. Auto-generate mobile number
        """
        print("\n" + "=" * 70)
        print("📱 MOBILE NUMBER INPUT")
        print("=" * 70)
        print("\nChoose an option:")
        print("  1. Enter mobile number manually")
        print("  2. Auto-generate mobile number")
        print()

        while True:
            choice = input("Enter your choice (1 or 2): ").strip()

            if choice == "1":
                return self._get_manual_mobile()
            elif choice == "2":
                mobile = generate_unique_mobile()
                print(f"\n✅ Auto-generated mobile number: {mobile}")
                self.allure_step("Mobile Input", "passed", {"mobile": mobile, "method": "auto-generated"})
                return mobile
            else:
                print("❌ Invalid choice! Please enter 1 or 2.")

    def _get_manual_mobile(self) -> str:
        """Get mobile number from user with validation"""
        while True:
            mobile = input("\nEnter 10-digit mobile number: ").strip()

            if len(mobile) != 10:
                print("❌ Error: Mobile number must be exactly 10 digits!")
                continue

            if not mobile.isdigit():
                print("❌ Error: Mobile number must contain only digits!")
                continue

            if mobile[0] not in ['6', '7', '8', '9']:
                print("❌ Error: Mobile number must start with 6, 7, 8, or 9!")
                continue

            print(f"✅ Mobile number accepted: {mobile}")
            self.allure_step("Mobile Input", "passed", {"mobile": mobile, "method": "manual"})
            return mobile

    def clear_and_setup(self):
        """Clear previous data and setup new test"""
        logger.info("=" * 70)
        logger.info("🚀 AUTO RUNNING COMPLETE 5-STAGE FLOW")
        logger.info("=" * 70)

        # Clear token store
        token_store.clear_all()
        logger.info("🗑️  Cleared previous session data")

        # Get mobile number from user
        self.mobile_number = self.get_mobile_number_from_user()

        # Generate email
        self.email = generate_random_email()

        self.report_data["test_data"] = {
            "mobile_number": self.mobile_number,
            "email": self.email,
            "otp_used": self.otp
        }

        logger.info(f"📱 Mobile Number: {self.mobile_number}")
        logger.info(f"📧 Auto-generated Email: {self.email}")
        logger.info(f"🔐 OTP: {self.otp}")
        logger.info("-" * 70)

        self.allure_step("Test Setup", "passed", {
            "mobile": self.mobile_number,
            "email": self.email,
            "otp": self.otp
        })

    def run_all_stages(self) -> bool:
        """Execute all 5 stages automatically"""
        test_status = "passed"
        error_message = ""

        # Start Allure test
        if self.allure_helper:
            self.allure_helper.start_test(
                "UAT_Onboarding Lead Generation",
                "In this flow we are generating the Lead user on UAT the flow will be Enter or auto generate the mobile number -> Generate and Verify Mobile OTP -> Generate and Verify Email OTP"
            )

        try:
            # Setup
            self.clear_and_setup()
            
            # Initialize client and stage manager
            self.client = UpstoxAuthClient()
            self.stage_manager = StageManager(self.client, self.mobile_number, self.email, self.otp)

            # Run all 5 stages
            stages = [
                ("Stage 1: Generate OTP", self.stage_manager.run_stage1_generate_otp),
                ("Stage 2: Verify OTP", self.stage_manager.run_stage2_verify_otp),
                ("Stage 3: 2FA Authentication", self.stage_manager.run_stage3_two_fa),
                ("Stage 4: Email Send OTP", self.stage_manager.run_stage4_email_send_otp),
                ("Stage 5: Email Verify OTP", self.stage_manager.run_stage5_email_verify_otp),
            ]

            for stage_name, stage_func in stages:
                result = stage_func()
                self.allure_step(stage_name, "passed" if result.success else "failed", result.details)
                
                if not result.success:
                    raise Exception(result.message)

            # Collect results
            self.report_data["api_results"] = self.stage_manager.get_results()
            self._update_summary()

            logger.info("\n" + "=" * 70)
            logger.info("✅ ALL 5 STAGES COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)

            return True

        except Exception as e:
            logger.error(f"\n❌ TEST FAILED: {e}")
            self.report_data["summary"]["overall_status"] = "FAIL"
            self.report_data["summary"]["error"] = str(e)
            test_status = "failed"
            error_message = str(e)
            return False

        finally:
            if self.client:
                self.client.close()

            # End Allure test
            if self.allure_helper:
                test_summary = self._prepare_test_summary()
                result_file = self.allure_helper.end_test(test_status, error_message, test_summary)
                print(f"\n📊 Allure result saved: {result_file}")

    def _update_summary(self):
        """Update test summary with final data"""
        all_data = self.client.get_all_stored_data() if self.client else {}
        user_data = all_data.get('user_data', {})

        self.report_data["summary"] = {
            "total_stages": 5,
            "passed": 5,
            "failed": 0,
            "success_rate": "100%",
            "overall_status": "PASS",
            "final_data": {
                "mobile_number": self.mobile_number,
                "email": self.email,
                "profile_id": user_data.get("profile_id"),
                "user_type": user_data.get("user_type"),
                "customer_status": user_data.get("customer_status"),
                "redirect_uri": user_data.get("redirect_uri"),
                "email_send_status": user_data.get("email_response"),
                "email_verify_status": user_data.get("email_verify_response")
            }
        }

    def _prepare_test_summary(self) -> dict:
        """Prepare test summary for Allure attachment"""
        final_data = self.report_data["summary"].get("final_data", {})
        return {
            "mobile_number": final_data.get("mobile_number"),
            "email": final_data.get("email"),
            "profile_id": final_data.get("profile_id"),
            "user_type": final_data.get("user_type"),
            "customer_status": final_data.get("customer_status"),
            "redirect_uri": final_data.get("redirect_uri"),
            "overall_status": self.report_data["summary"].get("overall_status"),
            "success_rate": self.report_data["summary"].get("success_rate"),
            "total_stages": self.report_data["summary"].get("total_stages"),
            "passed": self.report_data["summary"].get("passed"),
            "failed": self.report_data["summary"].get("failed")
        }

    def print_final_summary(self):
        """Print final console summary"""
        summary = self.report_data["summary"]
        final_data = summary.get("final_data", {})

        print("\n" + "=" * 80)
        print("📊 FINAL TEST REPORT".center(80))
        print("=" * 80)

        print("\n🎯 TEST DATA:")
        print("-" * 80)
        print(f"  📱 Mobile Number:     {final_data.get('mobile_number', 'N/A')}")
        print(f"  📧 Email:             {final_data.get('email', 'N/A')}")
        print(f"  🆔 Profile ID:        {final_data.get('profile_id', 'N/A')}")
        print(f"  👤 User Type:         {final_data.get('user_type', 'N/A')}")
        print(f"  📊 Customer Status:   {final_data.get('customer_status', 'N/A')}")

        print(f"\n📋 API TEST RESULTS:")
        print("-" * 80)
        print(f"  {'Stage':<8} {'API Name':<25} {'Testing Status'}")
        print("-" * 80)

        for result in self.report_data["api_results"]:
            print(f"  {result['stage']:<8} {result['api_name']:<25} ✅ {result['status']}")

        print("-" * 80)
        print(f"\n📈 SUMMARY:")
        print(f"  Total Stages:  {summary.get('total_stages', 0)}")
        print(f"  Passed:        ✅ {summary.get('passed', 0)}")
        print(f"  Failed:        ❌ {summary.get('failed', 0)}")
        print(f"  Success Rate:  {summary.get('success_rate', '0%')}")
        print(f"\n  Overall Status: ✅ ALL TESTS PASSED")

        if self.allure_enabled:
            print(f"\n  📊 Allure Report: View with 'allure serve reports/allure-results'")

        print("\n" + "=" * 80)
        print("🎉 EXECUTION COMPLETE!".center(80))
        print("=" * 80)
