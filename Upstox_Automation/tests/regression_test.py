#!/usr/bin/env python3
"""
REGRESSION TEST
Tests ALL mobile number validations (Invalid + Valid)
Includes: wrong format, wrong length, non-numeric, valid numbers
"""

import time
import random
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from validators.mobile_validator import MOBILE_TEST_CASES


def human_delay(min_sec=0.5, max_sec=1.5):
    """Add a short random delay."""
    time.sleep(random.uniform(min_sec, max_sec))


def type_like_human(element, text):
    """Type text with minimal delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.03))


class RegressionTester:
    """Regression test suite for mobile number validation"""
    
    def __init__(self):
        self.driver = None
        self.test_results = []
        self.url = "https://upstox.com/"
    
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
        print("🔍 Looking for mobile number input...")
        
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
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", mobile_input)
                human_delay(0.2, 0.4)
                mobile_input.click()
                human_delay(0.1, 0.2)
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
                
                try:
                    WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                except:
                    pass
                
                print("🖱️ Clicking Get OTP button...")
                ActionChains(self.driver).move_to_element(otp_button).click().perform()
                print("✅ Get OTP button clicked")
                human_delay(2, 3)
                return True
            except:
                continue
        return False
    
    def check_for_error_message(self):
        """Check if error message is displayed"""
        print("🔍 Checking for error messages...")
        
        time.sleep(1)
        specific_error = "Make sure your mobile number was entered correctly"
        
        error_xpaths = [
            f"//*[contains(text(), '{specific_error}')]",
            "//*[contains(text(), 'invalid') or contains(text(), 'Invalid')]",
            "//*[contains(text(), 'valid mobile') or contains(text(), 'Valid mobile')]",
            "//*[contains(text(), 'enter a valid') or contains(text(), 'Enter a valid')]",
            "//*[contains(text(), 'correctly') or contains(text(), 'Correctly')]",
            "//div[contains(@class, 'error')]",
            "//span[contains(@class, 'error')]",
            "//p[contains(@class, 'error')]",
            "//*[contains(@role, 'alert')]",
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
                        if error_text and len(error_text) > 5 and len(error_text) < 500:
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
        
        otp_indicators = [
            "//input[contains(@placeholder, 'OTP')]",
            "//input[contains(@id, 'otp')]",
            "//*[contains(text(), 'Enter OTP')]",
            "//*[contains(text(), 'Verify OTP')]",
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
    
    def test_mobile_number(self, mobile_number, expected_result, description=""):
        """Test a single mobile number"""
        print("\n" + "=" * 60)
        print(f"🧪 TESTING: Mobile Number '{mobile_number}'")
        print(f"📋 Expected: {expected_result}")
        if description:
            print(f"📝 Description: {description}")
        print("=" * 60)
        
        # Navigate to login page
        if not self.navigate_to_login():
            return {"mobile": mobile_number, "status": "ERROR", "reason": "Navigation failed"}
        
        # Enter mobile number
        if not self.enter_mobile_number(mobile_number):
            return {"mobile": mobile_number, "status": "ERROR", "reason": "Input not found"}
        
        # Click Get OTP
        if not self.click_get_otp():
            return {"mobile": mobile_number, "status": "ERROR", "reason": "Button not found"}
        
        # Check results
        errors = self.check_for_error_message()
        otp_screen = self.check_if_otp_screen_appears()
        
        # Determine actual result
        if errors and not otp_screen:
            actual_result = "FAIL"
        elif otp_screen and not errors:
            actual_result = "PASS"
        elif errors and otp_screen:
            actual_result = "AMBIGUOUS"
        else:
            actual_result = "UNKNOWN"
        
        test_passed = (actual_result == expected_result)
        
        result = {
            "mobile": mobile_number,
            "expected": expected_result,
            "actual": actual_result,
            "test_passed": test_passed,
            "errors": errors,
            "otp_screen": otp_screen,
            "description": description
        }
        
        if test_passed:
            print(f"✅ TEST PASSED")
        else:
            print(f"❌ TEST FAILED: Expected {expected_result}, got {actual_result}")
        
        return result
    
    def refresh_browser(self):
        """Refresh the browser"""
        print("\n🔄 Refreshing browser...")
        self.driver.refresh()
        human_delay(2, 3)
        print("✅ Browser refreshed")
    
    def run_regression_tests(self):
        """Run all regression tests - Invalid first, then Valid"""
        print("\n" + "=" * 70)
        print("🚀 REGRESSION TEST - MOBILE NUMBER VALIDATION")
        print("=" * 70)
        print("📱 Test Data Source: validators/mobile_validator.py")
        print("📝 Tests: 13 Invalid + 4 Valid = 17 Total")
        print("=" * 70)
        
        # Setup browser
        self.setup_browser()
        
        # PHASE 1: Test all INVALID mobile numbers first
        invalid_cases = MOBILE_TEST_CASES["invalid"]
        print(f"\n{'='*70}")
        print(f"🔴 PHASE 1: TESTING {len(invalid_cases)} INVALID MOBILE NUMBERS")
        print(f"{'='*70}")
        
        for i, case in enumerate(invalid_cases, 1):
            mobile = case["number"]
            expected = case["expected"]
            description = case.get("description", "")
            
            print(f"\n{'='*70}")
            print(f"📌 INVALID TEST {i}/{len(invalid_cases)}")
            print(f"{'='*70}")
            
            result = self.test_mobile_number(mobile, expected, description)
            result["phase"] = "INVALID"
            self.test_results.append(result)
            
            if i < len(invalid_cases):
                self.refresh_browser()
        
        # PHASE 2: Test all VALID mobile numbers
        valid_cases = MOBILE_TEST_CASES["valid"]
        print(f"\n{'='*70}")
        print(f"🟢 PHASE 2: TESTING {len(valid_cases)} VALID MOBILE NUMBERS")
        print(f"{'='*70}")
        
        self.refresh_browser()
        
        for i, case in enumerate(valid_cases, 1):
            mobile = case["number"]
            expected = case["expected"]
            description = case.get("description", "")
            
            print(f"\n{'='*70}")
            print(f"📌 VALID TEST {i}/{len(valid_cases)}")
            print(f"{'='*70}")
            
            result = self.test_mobile_number(mobile, expected, description)
            result["phase"] = "VALID"
            self.test_results.append(result)
            
            if i < len(valid_cases):
                self.refresh_browser()
        
        # Print final summary
        self.print_summary()
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 REGRESSION TEST SUMMARY")
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
            phase = result.get("phase", "UNKNOWN")
            
            status_icon = "✅" if test_passed else "❌"
            print(f"\n{i}. [{phase}] {status_icon} Mobile: '{mobile}'")
            print(f"   Expected: {expected} | Actual: {actual}")
            
            if result.get("errors"):
                print(f"   Error: {result['errors'][0]}")
            if result.get("otp_screen"):
                print(f"   OTP Screen: Yes")
        
        print("\n" + "=" * 70)
        print("✅ Regression testing complete. Browser remains open.")
        print("🔒 Close browser manually when done.")
        print("=" * 70)


def run_regression_test():
    """Main entry point for regression test"""
    tester = RegressionTester()
    
    try:
        results = tester.run_regression_tests()
        return {
            "test_type": "Regression",
            "status": "COMPLETE",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.get("test_passed")),
            "failed": sum(1 for r in results if not r.get("test_passed")),
            "results": results
        }
    except Exception as e:
        print(f"\n\n❌ Error during Regression test: {e}")
        import traceback
        traceback.print_exc()
        return {
            "test_type": "Regression",
            "status": "ERROR",
            "error": str(e)
        }


if __name__ == "__main__":
    result = run_regression_test()
    print(f"\nTest Result: {result['status']}")
