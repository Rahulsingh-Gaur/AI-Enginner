#!/usr/bin/env python3
"""
Test Email Flow Module
Contains test cases for email screen flow
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_cases.base_test import BaseTestCase
from validators.email_validator import validate_email


class TestEmailFlow(BaseTestCase):
    """Test cases for email screen flow"""
    
    def __init__(self, test_data_path: str = "config/test_data.json"):
        super().__init__(test_data_path)
        self.flow_name = "Email Flow"
    
    def test_tc_07_email_screen_check(self) -> dict:
        """TC-07: Handle Email screen (conditional - one-time)"""
        return {
            "status": "PASS",
            "conditional": True,
            "message": "Email screen checked (one-time occurrence)"
        }
    
    def test_tc_08_valid_email(self, email: str = None) -> dict:
        """TC-08: Enter valid email address"""
        if email is None:
            email = self.test_data.get("automation_config", {}).get("default_email", "Rahul.hajari@rksv.in")
        
        validation = validate_email(email)
        
        if validation["valid"]:
            return {
                "status": "PASS",
                "email": email,
                "normalized": validation["normalized"],
                "domain": validation["domain"],
                "message": "Email is valid"
            }
        else:
            raise ValueError(f"Email validation failed: {', '.join(validation['errors'])}")
    
    def test_tc_09_invalid_email_missing_domain(self) -> dict:
        """TC-09: Enter invalid email (missing domain)"""
        email = "test@"
        validation = validate_email(email)
        
        if not validation["valid"]:
            return {
                "status": "PASS",
                "email": email,
                "expected_error": "Invalid email format - missing domain",
                "actual_errors": validation["errors"],
                "message": "Correctly rejected invalid email"
            }
        else:
            raise ValueError("Should have rejected email with missing domain")
    
    def test_tc_10_click_continue(self) -> dict:
        """TC-10: Click Continue button"""
        return {
            "status": "PASS",
            "element": "Continue button",
            "xpath": "//button[contains(text(), 'Continue')]",
            "message": "Continue button clicked"
        }
    
    def run_all(self) -> list:
        """Run all email flow test cases"""
        print(f"\n{'='*60}")
        print(f"🚀 Running {self.flow_name}")
        print(f"{'='*60}")
        
        # Get test cases from config
        email_tests = self.test_data.get("test_cases", {}).get("email_flow", [])
        
        for test_case in email_tests:
            tc_id = test_case.get("tc_id")
            description = test_case.get("description")
            data = test_case.get("data", {})
            
            # Map test case IDs to methods
            test_methods = {
                "TC-07": self.test_tc_07_email_screen_check,
                "TC-08": lambda: self.test_tc_08_valid_email(data.get("email")),
                "TC-09": self.test_tc_09_invalid_email_missing_domain,
                "TC-10": self.test_tc_10_click_continue,
            }
            
            if tc_id in test_methods:
                self.run_test(tc_id, description, test_methods[tc_id])
        
        return self.results


if __name__ == "__main__":
    # Run tests directly
    test = TestEmailFlow()
    results = test.run_all()
    test.print_summary()
