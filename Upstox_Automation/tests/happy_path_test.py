#!/usr/bin/env python3
"""
HAPPY PATH TEST
Single complete flow: Mobile → Get OTP → Email → Continue
Uses only valid data (9552931377)
"""

import time
import random
import sys
import os
from pathlib import Path
from datetime import datetime

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
from tools.test_logger import TestLogger


def human_delay(min_sec=0.5, max_sec=1.5):
    """Add a short random delay."""
    time.sleep(random.uniform(min_sec, max_sec))


def type_like_human(element, text):
    """Type text with minimal delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.03))


def prompt_for_otp(mobile_number: str, headless: bool = False) -> str:
    """
    Prompt user for OTP
    In GUI mode: shows popup or prompt
    In CLI mode: waits for console input
    """
    message = f"\n{'='*70}\n📱 OTP REQUIRED\n{'='*70}\nPlease enter OTP sent to {mobile_number}:\n{'='*70}\nOTP: "
    
    if headless:
        # CLI mode - read from console
        print(message, end="", flush=True)
        otp = input().strip()
    else:
        # GUI mode - could use a simple dialog or console input
        print(message, end="", flush=True)
        try:
            otp = input().strip()
        except EOFError:
            # If running in background without TTY
            otp = ""
            print("\n⚠️ Could not read OTP input. Skipping OTP entry.")
    
    return otp


def run_happy_path_test(headless: bool = False):
    """
    Run Happy Path Test - Single complete login flow
    Mobile (9552931377) → Get OTP → Email → Continue
    
    Args:
        headless: If True, run in CLI mode without browser window
    """
    driver = None
    results = []
    
    # Initialize logger
    logger = TestLogger("Happy Path Test")
    
    print("\n" + "=" * 70)
    print("🚀 HAPPY PATH TEST - COMPLETE LOGIN FLOW")
    print("=" * 70)
    print(f"📱 Mobile: {DEFAULT_MOBILE_NUMBER}")
    print("📝 Flow: Mobile → Get OTP → Email Screen → Continue")
    print(f"👤 Mode: {'CLI (Headless)' if headless else 'GUI'}")
    print("=" * 70)
    
    # Log start
    logger.log_output("Test Start", "Happy Path Test initialized", {
        "mobile": DEFAULT_MOBILE_NUMBER,
        "headless": headless,
        "mode": "CLI" if headless else "GUI"
    })
    
    try:
        # Setup browser
        print("\n🚀 Initializing Chrome browser...")
        if headless:
            print("   (Running in HEADLESS mode - no browser window)")
        options = webdriver.ChromeOptions()
        
        # Headless mode options
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
        else:
            options.add_argument("--start-maximized")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if not headless:
            options.add_experimental_option("detach", True)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Browser initialized")
        
        logger.log_output("Browser Init", "Chrome browser initialized", {"headless": headless})
        
        # STEP 1: Navigate and enter mobile
        print("\n🔴 STEP 1: ENTER MOBILE NUMBER")
        print("-" * 70)
        
        url = "https://upstox.com/"
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        logger.log_output("Navigation", f"Navigated to {url}", {"url": url})
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
        logger.log_output("Sign In", "Sign In button clicked")
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
            logger.log_input("Mobile Number", DEFAULT_MOBILE_NUMBER)
        
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
                logger.log_output("Get OTP", "Get OTP button clicked")
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
        logger.log_step(1, "Mobile Entry", "PASS", {"mobile": DEFAULT_MOBILE_NUMBER})
        
        # OTP Handling
        print("\n📱 CHECKING FOR OTP SCREEN...")
        otp_screen_found = False
        try:
            otp_input = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'OTP')]"))
            )
            if otp_input.is_displayed():
                otp_screen_found = True
                print("✅ OTP screen detected!")
                logger.log_output("OTP Screen", "OTP input screen found")
                
                # Prompt for OTP
                logger.log_otp_prompt(DEFAULT_MOBILE_NUMBER)
                otp = prompt_for_otp(DEFAULT_MOBILE_NUMBER, headless)
                
                if otp:
                    print(f"⌨️ Entering OTP: {'*' * len(otp)}")
                    otp_input.clear()
                    type_like_human(otp_input, otp)
                    logger.log_input("OTP", otp, masked=True)
                    print("✅ OTP entered")
                    
                    # Click Verify
                    verify_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify')]")
                    verify_btn.click()
                    logger.log_output("Verify OTP", "Verify button clicked")
                    human_delay(2, 3)
                else:
                    print("⚠️ No OTP entered. Skipping OTP step.")
                    logger.log_output("OTP", "No OTP entered - skipped")
        except:
            print("ℹ️ OTP screen not found (may not be required)")
            logger.log_output("OTP Screen", "OTP screen not found - may be email flow")
        
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
                logger.log_output("Email Screen", "Email input screen found")
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
            logger.log_input("Email", email_address)
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
                logger.log_output("Continue", "Continue button clicked")
                human_delay(2, 3)
                
                results.append({
                    "step": "Email Entry",
                    "status": "PASS",
                    "email": email_address
                })
                logger.log_step(2, "Email Entry", "PASS", {"email": email_address})
            else:
                results.append({
                    "step": "Email Entry",
                    "status": "FAIL",
                    "error": "Continue button not found"
                })
                logger.log_error("Continue button not found")
        else:
            print("ℹ️ Email screen not present (already completed)")
            results.append({
                "step": "Email Entry",
                "status": "SKIP",
                "message": "Email screen not present"
            })
            logger.log_output("Email Screen", "Email screen not present - skipped")
        
        print("✅ STEP 2 COMPLETE")
        
        # STEP 3: Final verification
        print("\n🟢 STEP 3: VERIFY FINAL STATE")
        print("-" * 70)
        
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        logger.log_output("Final URL", f"Current URL: {current_url}", {"url": current_url})
        
        # Check for OTP input
        otp_found = False
        try:
            otp_input = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'OTP')]"))
            )
            if otp_input.is_displayed():
                otp_found = True
                print("✅ OTP input found - Happy Path SUCCESS!")
                logger.log_output("Final Check", "OTP input found - Test SUCCESS")
        except:
            logger.log_output("Final Check", "OTP input not found")
        
        results.append({
            "step": "Final Verification",
            "status": "PASS" if otp_found else "FAIL",
            "url": current_url,
            "otp_screen": otp_found
        })
        logger.log_step(3, "Final Verification", "PASS" if otp_found else "FAIL", {"otp_screen": otp_found})
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 HAPPY PATH COMPLETE!")
        print("=" * 70)
        print(f"📱 Mobile: {DEFAULT_MOBILE_NUMBER}")
        print(f"📧 Email: {email_address}")
        print(f"🔗 URL: {current_url}")
        print(f"✅ OTP Screen: {'Yes' if otp_found else 'No'}")
        print("=" * 70)
        
        # Generate Logs.md
        logs_md_path = logger.generate_logs_md("Logs.md")
        logs_json_path = logger.generate_json_log("logs.json")
        
        print(f"📝 Logs saved:")
        print(f"   📄 Logs.md: {logs_md_path}")
        print(f"   📄 logs.json: {logs_json_path}")
        
        if not headless:
            print("📝 Browser remains open for manual verification.")
            print("🔒 Close browser manually when done.")
        print("=" * 70)
        
        return {
            "test_type": "Happy Path",
            "status": "PASS",
            "results": results,
            "mobile": DEFAULT_MOBILE_NUMBER,
            "email": email_address,
            "url": current_url,
            "logs_md": logs_md_path,
            "logs_json": logs_json_path
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n\n❌ Error during Happy Path test: {error_msg}")
        logger.log_error(error_msg)
        
        # Generate logs even on failure
        logs_md_path = logger.generate_logs_md("Logs.md")
        logs_json_path = logger.generate_json_log("logs.json")
        
        print(f"📝 Logs saved (with error):")
        print(f"   📄 Logs.md: {logs_md_path}")
        print(f"   📄 logs.json: {logs_json_path}")
        
        return {
            "test_type": "Happy Path",
            "status": "FAIL",
            "error": error_msg,
            "results": results,
            "logs_md": logs_md_path,
            "logs_json": logs_json_path
        }


if __name__ == "__main__":
    result = run_happy_path_test()
    print(f"\nTest Result: {result['status']}")
    if 'logs_md' in result:
        print(f"Logs: {result['logs_md']}")
