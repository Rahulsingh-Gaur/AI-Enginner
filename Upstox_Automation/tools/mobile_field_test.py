#!/usr/bin/env python3
"""
Mobile Number Field In-Depth Testing
Tests multiple mobile numbers on actual website with browser refresh between each test

MOBILE NUMBERS: Imported from validators/mobile_validator.py (Single Source of Truth)
"""

import time
import random
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Import mobile test cases from single source of truth
from validators.mobile_validator import (
    get_mobile_numbers_for_browser_test, 
    DEFAULT_MOBILE_NUMBER,
    MOBILE_TEST_CASES
)


def human_delay(min_sec=0.5, max_sec=1.5):
    """Add a short random delay."""
    time.sleep(random.uniform(min_sec, max_sec))


def type_like_human(element, text):
    """Type text with minimal delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.03))


class MobileFieldTester:
    """Test mobile number field with various inputs"""
    
    def __init__(self, happy_path_only: bool = False):
        """
        Initialize tester
        
        Args:
            happy_path_only: If True, only test VALID mobile numbers (skip invalid validation)
        """
        self.driver = None
        self.test_results = []
        self.url = "https://upstox.com/"
        self.happy_path_only = happy_path_only
    
    def setup_browser(self):
        """Initialize Chrome browser"""
        print("🚀 Initializing Chrome browser...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Browser initialized")
    
    def navigate_to_login(self):
        """Navigate to Upstox and click Sign In"""
        print(f"🌐 Navigating to: {self.url}")
        self.driver.get(self.url)
        human_delay(1, 2)
        
        # Find and click Sign In
        print("🔍 Looking for Sign In button...")
        xpaths_signin = [
            "//a[contains(text(), 'Sign In')]",
            "//button[contains(text(), 'Sign In')]",
        ]
        
        for xpath in xpaths_signin:
            try:
                signin = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", signin)
                human_delay(0.3, 0.6)
                ActionChains(self.driver).move_to_element(signin).click().perform()
                print("✅ Sign In button clicked")
                human_delay(1, 2)
                return True
            except:
                continue
        
        return False
    
    def enter_mobile_number(self, mobile_number):
        """Enter mobile number in the input field"""
        print(f"🔍 Looking for mobile number input...")
        
        xpaths_mobile = [
            "//input[@type='tel']",
            "//input[contains(@id, 'mobile')]",
            "//input[contains(@placeholder, 'mobile')]",
        ]
        
        for xpath in xpaths_mobile:
            try:
                mobile_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                
                # Scroll and focus
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", mobile_input)
                human_delay(0.2, 0.4)
                mobile_input.click()
                human_delay(0.1, 0.2)
                
                # Clear and enter
                mobile_input.clear()
                human_delay(0.1, 0.2)
                
                print(f"⌨️ Entering mobile number: {mobile_number}")
                type_like_human(mobile_input, mobile_number)
                print("✅ Mobile number entered")
                human_delay(0.5, 1)
                return True
            except:
                continue
        
        return False
    
    def click_get_otp(self):
        """Click Get OTP button"""
        print("🔍 Looking for Get OTP button...")
        
        xpaths_otp = [
            "//button[contains(text(), 'Get OTP')]",
            "//button[contains(text(), 'GET OTP')]",
        ]
        
        for xpath in xpaths_otp:
            try:
                otp_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", otp_button)
                human_delay(0.2, 0.4)
                
                # Wait for button to be enabled
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                except:
                    pass
                
                print("🖱️ Clicking Get OTP button...")
                ActionChains(self.driver).move_to_element(otp_button).click().perform()
                print("✅ Get OTP button clicked")
                human_delay(2, 3)  # Wait for response
                return True
            except:
                continue
        
        return False
    
    def check_for_error_message(self):
        """Check if error message is displayed"""
        print("🔍 Checking for error messages...")
        
        # Wait a bit for error message to appear
        time.sleep(1)
        
        # Specific error message we're looking for
        specific_error = "Make sure your mobile number was entered correctly"
        
        # Common error message XPaths - expanded list
        error_xpaths = [
            # Specific error message
            f"//*[contains(text(), '{specific_error}')]",
            # Generic error patterns
            "//*[contains(text(), 'invalid') or contains(text(), 'Invalid')]",
            "//*[contains(text(), 'valid mobile') or contains(text(), 'Valid mobile')]",
            "//*[contains(text(), 'enter a valid') or contains(text(), 'Enter a valid')]",
            "//*[contains(text(), 'correctly') or contains(text(), 'Correctly')]",
            "//*[contains(text(), 'mobile number') or contains(text(), 'Mobile number')]",
            "//*[contains(text(), 'check') or contains(text(), 'Check')]",
            # Error element classes
            "//div[contains(@class, 'error')]",
            "//span[contains(@class, 'error')]",
            "//p[contains(@class, 'error')]",
            "//div[contains(@class, 'Error')]",
            "//*[contains(@role, 'alert')]",
            "//*[contains(@class, 'toast')]",
            "//*[contains(@class, 'notification')]",
            "//*[contains(@class, 'message-error')]",
            # By color (red text often indicates error)
            "//*[contains(@style, 'color: red')]",
            "//*[contains(@style, 'color:red')]",
        ]
        
        errors_found = []
        
        # First check for the specific error message
        try:
            specific_elem = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{specific_error}')]")
            if specific_elem.is_displayed():
                error_text = specific_elem.text.strip()
                errors_found.append(error_text)
                print(f"✅ Specific error found: {error_text}")
                return errors_found
        except:
            pass
        
        # Then check other error patterns
        for xpath in error_xpaths:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for elem in elements:
                    if elem.is_displayed():
                        error_text = elem.text.strip()
                        # Filter out short or empty texts
                        if error_text and len(error_text) > 5 and len(error_text) < 500:
                            # Avoid duplicates
                            if error_text not in errors_found:
                                errors_found.append(error_text)
                                print(f"⚠️ Error found: {error_text}")
            except:
                continue
        
        if not errors_found:
            print("ℹ️ No error messages found")
        
        return errors_found
    
    def check_if_otp_screen_appears(self):
        """Check if we moved to OTP screen"""
        print("🔍 Checking if OTP screen appeared...")
        
        # Check for OTP input or OTP-related text
        otp_indicators = [
            "//input[contains(@placeholder, 'OTP')]",
            "//input[contains(@id, 'otp')]",
            "//*[contains(text(), 'Enter OTP')]",
            "//*[contains(text(), 'Verify OTP')]",
            "//*[contains(text(), 'One Time Password')]",
        ]
        
        for xpath in otp_indicators:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if element.is_displayed():
                    print("✅ OTP screen detected!")
                    return True
            except:
                continue
        
        return False
    
    def test_mobile_number(self, mobile_number, expected_result):
        """
        Test a single mobile number
        
        Args:
            mobile_number: The mobile number to test
            expected_result: "PASS" (should go to OTP) or "FAIL" (should show error)
        """
        print("\n" + "=" * 60)
        print(f"🧪 TESTING: Mobile Number '{mobile_number}'")
        print(f"📋 Expected: {expected_result}")
        print("=" * 60)
        
        # Navigate to login page
        if not self.navigate_to_login():
            print("❌ Failed to navigate to login page")
            return {"mobile": mobile_number, "status": "ERROR", "reason": "Navigation failed"}
        
        # Enter mobile number
        if not self.enter_mobile_number(mobile_number):
            print("❌ Failed to enter mobile number")
            return {"mobile": mobile_number, "status": "ERROR", "reason": "Input not found"}
        
        # Click Get OTP
        if not self.click_get_otp():
            print("❌ Failed to click Get OTP")
            return {"mobile": mobile_number, "status": "ERROR", "reason": "Button not found"}
        
        # Check results
        errors = self.check_for_error_message()
        otp_screen = self.check_if_otp_screen_appears()
        
        # Determine actual result
        if errors and not otp_screen:
            actual_result = "FAIL"
            print(f"❌ Result: Error displayed - {errors[0] if errors else 'Unknown error'}")
        elif otp_screen and not errors:
            actual_result = "PASS"
            print("✅ Result: Moved to OTP screen successfully")
        elif errors and otp_screen:
            actual_result = "AMBIGUOUS"
            print(f"⚠️ Result: Both error and OTP screen detected")
        else:
            actual_result = "UNKNOWN"
            print("⚠️ Result: Could not determine outcome")
        
        # Compare with expected
        test_passed = (actual_result == expected_result)
        
        result = {
            "mobile": mobile_number,
            "expected": expected_result,
            "actual": actual_result,
            "test_passed": test_passed,
            "errors": errors,
            "otp_screen": otp_screen
        }
        
        if test_passed:
            print(f"✅ TEST PASSED: Behavior matches expectation")
        else:
            print(f"❌ TEST FAILED: Expected {expected_result}, got {actual_result}")
        
        return result
    
    def refresh_browser(self):
        """Refresh the browser"""
        print("\n🔄 Refreshing browser...")
        self.driver.refresh()
        human_delay(2, 3)
        print("✅ Browser refreshed")
    
    def run_all_tests(self):
        """Run mobile number tests based on mode"""
        print("\n" + "=" * 70)
        print("🚀 MOBILE NUMBER FIELD IN-DEPTH TESTING")
        print("=" * 70)
        print("📱 Test Data Source: validators/mobile_validator.py")
        
        if self.happy_path_only:
            print("🟢 MODE: HAPPY PATH ONLY (Valid numbers only, skip validation)")
        else:
            print("📝 MODE: FULL VALIDATION (Invalid first, then Valid)")
        print("=" * 70)
        
        # Setup browser
        self.setup_browser()
        
        # Get test cases from single source of truth
        from validators.mobile_validator import MOBILE_TEST_CASES
        
        # PHASE 1: Test all INVALID mobile numbers first (skip if happy_path_only)
        if not self.happy_path_only:
            invalid_cases = MOBILE_TEST_CASES["invalid"]
            print(f"\n{'='*70}")
            print(f"🔴 PHASE 1: TESTING {len(invalid_cases)} INVALID MOBILE NUMBERS")
            print(f"{'='*70}")
            
            for i, case in enumerate(invalid_cases, 1):
                mobile = case["number"]
                expected = case["expected"]  # Should be "FAIL"
                description = case.get("description", "")
                
                print(f"\n{'='*70}")
                print(f"📌 INVALID TEST {i}/{len(invalid_cases)}")
                print(f"   Mobile: {mobile}")
                print(f"   Expected: Error message should appear")
                print(f"{'='*70}")
                
                result = self.test_mobile_number(mobile, expected)
                result["phase"] = "INVALID"
                result["description"] = f"[INVALID] {description}"
                self.test_results.append(result)
                
                # Refresh browser for next test (except last invalid case)
                if i < len(invalid_cases):
                    self.refresh_browser()
            
            # Refresh once before starting valid cases
            self.refresh_browser()
        
        # PHASE 2: Test all VALID mobile numbers (Happy Path)
        valid_cases = MOBILE_TEST_CASES["valid"]
        print(f"\n{'='*70}")
        print(f"🟢 PHASE 2: TESTING {len(valid_cases)} VALID MOBILE NUMBERS")
        print(f"{'='*70}")
        
        if self.happy_path_only:
            print("   (Happy Path Mode - Testing only valid numbers)")
        
        for i, case in enumerate(valid_cases, 1):
            mobile = case["number"]
            expected = case["expected"]  # Should be "PASS"
            description = case.get("description", "")
            
            print(f"\n{'='*70}")
            print(f"📌 VALID TEST {i}/{len(valid_cases)}")
            print(f"   Mobile: {mobile}")
            print(f"   Expected: OTP screen should appear")
            print(f"{'='*70}")
            
            result = self.test_mobile_number(mobile, expected)
            result["phase"] = "VALID"
            result["description"] = f"[VALID] {description}"
            self.test_results.append(result)
            
            # Refresh browser for next test (except last valid case)
            if i < len(valid_cases):
                self.refresh_browser()
        
        # Print final summary
        self.print_summary()
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 70)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get("test_passed"))
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Pass Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        print("\n" + "-" * 70)
        print("DETAILED RESULTS:")
        print("-" * 70)
        
        for i, result in enumerate(self.test_results, 1):
            mobile = result.get("mobile", "N/A")
            expected = result.get("expected", "N/A")
            actual = result.get("actual", "N/A")
            test_passed = result.get("test_passed", False)
            
            status_icon = "✅" if test_passed else "❌"
            print(f"\n{i}. {status_icon} Mobile: {mobile}")
            print(f"   Expected: {expected} | Actual: {actual}")
            
            if result.get("errors"):
                print(f"   Error Message: {result['errors'][0]}")
            if result.get("otp_screen"):
                print(f"   OTP Screen: Yes")
        
        print("\n" + "=" * 70)
        print("✅ Testing complete. Browser remains open.")
        print("🔒 Close browser manually when done.")
        print("=" * 70)
    
    def run_happy_path_complete_flow(self):
        """
        Run complete happy path flow with single mobile number
        Mobile → OTP → Email → Continue
        """
        from validators.email_validator import validate_email
        
        print("\n" + "=" * 70)
        print("🚀 HAPPY PATH - COMPLETE LOGIN FLOW")
        print("=" * 70)
        print(f"📱 Mobile: {DEFAULT_MOBILE_NUMBER}")
        print("📝 Flow: Mobile → Get OTP → Email Screen → Continue")
        print("=" * 70)
        
        # Setup browser
        self.setup_browser()
        
        # STEP 1: Navigate and enter mobile
        print("\n🔴 STEP 1: ENTER MOBILE NUMBER")
        print("-" * 70)
        
        if not self.navigate_to_login():
            print("❌ Failed to navigate")
            return
        
        if not self.enter_mobile_number(DEFAULT_MOBILE_NUMBER):
            print("❌ Failed to enter mobile")
            return
        
        if not self.click_get_otp():
            print("❌ Failed to click Get OTP")
            return
        
        print("✅ STEP 1 COMPLETE: Mobile number accepted")
        
        # STEP 2: Check for Email Screen (conditional)
        print("\n🟡 STEP 2: CHECK FOR EMAIL SCREEN")
        print("-" * 70)
        
        human_delay(2, 3)
        
        email_address = "Rahul.hajari@rksv.in"
        email_screen_found = False
        
        # Check for email screen
        xpaths_email_input = [
            "//input[@placeholder='Enter your email address']",
            "//input[contains(@placeholder, 'email')]",
            "//input[@type='email']",
        ]
        
        email_input = None
        for xpath in xpaths_email_input:
            try:
                email_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                email_screen_found = True
                print("✅ Email screen found!")
                break
            except:
                continue
        
        if email_screen_found and email_input:
            # Enter email
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
            human_delay(0.3, 0.6)
            email_input.click()
            human_delay(0.2, 0.4)
            email_input.clear()
            human_delay(0.1, 0.2)
            
            print(f"⌨️ Entering email: {email_address}")
            type_like_human(email_input, email_address)
            print("✅ Email entered!")
            human_delay(0.5, 1)
            
            # Click Continue
            print("🔍 Looking for Continue button...")
            xpaths_continue = [
                "//button[contains(text(), 'Continue')]",
                "//button[@type='submit']",
            ]
            
            continue_btn = None
            for xpath in xpaths_continue:
                try:
                    continue_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    print("✅ Continue button found")
                    break
                except:
                    continue
            
            if continue_btn:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
                human_delay(0.3, 0.6)
                print("🖱️ Clicking Continue...")
                ActionChains(self.driver).move_to_element(continue_btn).click().perform()
                print("✅ Continue clicked!")
                human_delay(2, 3)
            else:
                print("⚠️ Continue button not found")
        else:
            print("ℹ️ Email screen not present (already completed)")
        
        print("✅ STEP 2 COMPLETE")
        
        # STEP 3: Final verification
        print("\n🟢 STEP 3: VERIFY FINAL STATE")
        print("-" * 70)
        
        # Check current URL or page state
        current_url = self.driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        # Check for OTP input (success indicator)
        otp_found = False
        try:
            otp_input = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'OTP')]"))
            )
            if otp_input.is_displayed():
                otp_found = True
                print("✅ OTP input found - Happy Path SUCCESS!")
        except:
            pass
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 HAPPY PATH COMPLETE!")
        print("=" * 70)
        print(f"📱 Mobile: {DEFAULT_MOBILE_NUMBER}")
        print(f"📧 Email: {email_address}")
        print(f"🔗 URL: {current_url}")
        print(f"✅ OTP Screen: {'Yes' if otp_found else 'No'}")
        print("=" * 70)
        print("📝 Browser remains open for manual verification.")
        print("🔒 Close browser manually when done.")
        print("=" * 70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mobile Number Field Browser Testing")
    parser.add_argument(
        "--happy-path", "-hp",
        action="store_true",
        help="Run complete happy path flow (Mobile → OTP → Email → Continue) with default mobile"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["full", "happy", "complete"],
        default="full",
        help="Test mode: full=all tests, happy=valid only, complete=single happy path flow"
    )
    
    args = parser.parse_args()
    
    # Create tester
    tester = MobileFieldTester(happy_path_only=args.happy_path)
    
    try:
        # Determine which test to run
        if args.mode == "complete" or args.happy_path:
            # Run complete happy path flow (single mobile, full flow)
            tester.run_happy_path_complete_flow()
        else:
            # Run all tests (invalid + valid)
            tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    return tester.test_results


if __name__ == "__main__":
    main()
