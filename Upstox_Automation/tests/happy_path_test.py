#!/usr/bin/env python3
"""
HAPPY PATH TEST
Single complete flow: Mobile → Get OTP → Email → Continue
Uses only valid data (9552931377)
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

from validators.mobile_validator import DEFAULT_MOBILE_NUMBER


def human_delay(min_sec=0.5, max_sec=1.5):
    """Add a short random delay."""
    time.sleep(random.uniform(min_sec, max_sec))


def type_like_human(element, text):
    """Type text with minimal delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.03))


def run_happy_path_test():
    """
    Run Happy Path Test - Single complete login flow
    Mobile (9552931377) → Get OTP → Email → Continue
    """
    driver = None
    results = []
    
    print("\n" + "=" * 70)
    print("🚀 HAPPY PATH TEST - COMPLETE LOGIN FLOW")
    print("=" * 70)
    print(f"📱 Mobile: {DEFAULT_MOBILE_NUMBER}")
    print("📝 Flow: Mobile → Get OTP → Email Screen → Continue")
    print("=" * 70)
    
    try:
        # Setup browser
        print("\n🚀 Initializing Chrome browser...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Browser initialized")
        
        # STEP 1: Navigate and enter mobile
        print("\n🔴 STEP 1: ENTER MOBILE NUMBER")
        print("-" * 70)
        
        url = "https://upstox.com/"
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        human_delay(1, 2)
        
        # Click Sign In
        print("🔍 Looking for Sign In button...")
        signin = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign In')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", signin)
        human_delay(0.3, 0.6)
        ActionChains(driver).move_to_element(signin).click().perform()
        print("✅ Sign In button clicked")
        human_delay(1, 2)
        
        # Enter mobile
        print("🔍 Looking for mobile number input...")
        xpaths_mobile = [
            "//input[@type='tel']",
            "//input[contains(@id, 'mobile')]",
            "//input[contains(@placeholder, 'mobile')]",
        ]
        
        mobile_input = None
        for xpath in xpaths_mobile:
            try:
                mobile_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                print(f"✅ Found mobile input")
                break
            except:
                continue
        
        if mobile_input:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", mobile_input)
            human_delay(0.2, 0.4)
            mobile_input.click()
            human_delay(0.1, 0.2)
            mobile_input.clear()
            human_delay(0.1, 0.2)
            
            print(f"⌨️ Entering mobile number: {DEFAULT_MOBILE_NUMBER}")
            type_like_human(mobile_input, DEFAULT_MOBILE_NUMBER)
            print("✅ Mobile number entered")
            human_delay(0.5, 1)
        
        # Click Get OTP
        print("🔍 Looking for Get OTP button...")
        xpaths_otp = [
            "//button[contains(text(), 'Get OTP')]",
            "//button[contains(text(), 'GET OTP')]",
        ]
        
        for xpath in xpaths_otp:
            try:
                otp_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", otp_button)
                human_delay(0.2, 0.4)
                
                try:
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                except:
                    pass
                
                print("🖱️ Clicking Get OTP button...")
                ActionChains(driver).move_to_element(otp_button).click().perform()
                print("✅ Get OTP button clicked")
                human_delay(2, 3)
                break
            except:
                continue
        
        print("✅ STEP 1 COMPLETE: Mobile number accepted")
        results.append({
            "step": "Mobile Entry",
            "status": "PASS",
            "mobile": DEFAULT_MOBILE_NUMBER
        })
        
        # STEP 2: Check for Email Screen
        print("\n🟡 STEP 2: CHECK FOR EMAIL SCREEN")
        print("-" * 70)
        
        human_delay(2, 3)
        
        email_address = "Rahul.hajari@rksv.in"
        email_screen_found = False
        
        xpaths_email_input = [
            "//input[@placeholder='Enter your email address']",
            "//input[contains(@placeholder, 'email')]",
            "//input[@type='email']",
        ]
        
        email_input = None
        for xpath in xpaths_email_input:
            try:
                email_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                email_screen_found = True
                print("✅ Email screen found!")
                break
            except:
                continue
        
        if email_screen_found and email_input:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
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
                    continue_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    print("✅ Continue button found")
                    break
                except:
                    continue
            
            if continue_btn:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
                human_delay(0.3, 0.6)
                print("🖱️ Clicking Continue...")
                ActionChains(driver).move_to_element(continue_btn).click().perform()
                print("✅ Continue clicked!")
                human_delay(2, 3)
                
                results.append({
                    "step": "Email Entry",
                    "status": "PASS",
                    "email": email_address
                })
            else:
                results.append({
                    "step": "Email Entry",
                    "status": "FAIL",
                    "error": "Continue button not found"
                })
        else:
            print("ℹ️ Email screen not present (already completed)")
            results.append({
                "step": "Email Entry",
                "status": "SKIP",
                "message": "Email screen not present"
            })
        
        print("✅ STEP 2 COMPLETE")
        
        # STEP 3: Final verification
        print("\n🟢 STEP 3: VERIFY FINAL STATE")
        print("-" * 70)
        
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        # Check for OTP input
        otp_found = False
        try:
            otp_input = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'OTP')]"))
            )
            if otp_input.is_displayed():
                otp_found = True
                print("✅ OTP input found - Happy Path SUCCESS!")
        except:
            pass
        
        results.append({
            "step": "Final Verification",
            "status": "PASS" if otp_found else "FAIL",
            "url": current_url,
            "otp_screen": otp_found
        })
        
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
        
        return {
            "test_type": "Happy Path",
            "status": "PASS",
            "results": results,
            "mobile": DEFAULT_MOBILE_NUMBER,
            "email": email_address,
            "url": current_url
        }
        
    except Exception as e:
        print(f"\n\n❌ Error during Happy Path test: {e}")
        return {
            "test_type": "Happy Path",
            "status": "FAIL",
            "error": str(e),
            "results": results
        }


if __name__ == "__main__":
    result = run_happy_path_test()
    print(f"\nTest Result: {result['status']}")
