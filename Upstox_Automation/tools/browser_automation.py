#!/usr/bin/env python3
"""
Browser Automation Tool using Selenium
Opens Chrome, navigates to Upstox, clicks Sign In, enters mobile number, 
handles Cloudflare checkbox, enters email (if screen appears), keeps browser open.

MOBILE NUMBER: Imported from validators/mobile_validator.py (Single Source of Truth)
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

# Import default mobile number from single source of truth
from validators.mobile_validator import DEFAULT_MOBILE_NUMBER


def human_delay(min_sec=0.5, max_sec=1.5):
    """Add a short random delay to simulate human behavior (optimized)."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def type_like_human(element, text):
    """Type text with minimal delays between characters (fast but human-like)."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.03))  # 10-30ms per character


def open_browser_and_login(url: str = "https://upstox.com/", mobile_number: str = DEFAULT_MOBILE_NUMBER) -> None:
    """
    Open Chrome browser, navigate to Upstox, click Sign In, 
    enter mobile number, handle Cloudflare checkbox, handle email screen (conditional),
    keep browser open.
    
    Args:
        url: Target URL to navigate to
        mobile_number: Mobile number to enter in login form
    """
    driver = None
    try:
        print(f"🚀 Initializing Chrome browser...")
        
        # Setup Chrome options - keep browser open and anti-detection
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # Detach keeps browser open after script ends
        options.add_experimental_option("detach", True)
        
        # Initialize driver with automatic ChromeDriver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Remove navigator.webdriver flag to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load (reduced)
        print("⏳ Waiting for page to load...")
        human_delay(1, 2)
        
        # ============================================
        # STEP 1: Find and click Sign In button
        # ============================================
        print("🔍 STEP 1: Looking for Sign In button...")
        
        xpaths_signin = [
            "//a[contains(text(), 'Sign In')]",
            "//button[contains(text(), 'Sign In')]",
            "//a[contains(@href, 'login')]",
            "//button[contains(@class, 'signin')]",
        ]
        
        signin_element = None
        for xpath in xpaths_signin:
            try:
                signin_element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                print(f"✅ Found Sign In button using XPath: {xpath}")
                break
            except:
                continue
        
        if signin_element:
            # Scroll into view and click like human
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", signin_element)
            human_delay(0.3, 0.6)
            print("🖱️ Clicking Sign In button...")
            ActionChains(driver).move_to_element(signin_element).click().perform()
            print("✅ Sign In button clicked!")
            human_delay(1, 2)  # Wait for login page (reduced)
        else:
            print("⚠️ Sign In button not found")
            driver.save_screenshot(".tmp/signin_not_found.png")
            return
        
        # ============================================
        # STEP 2: Enter mobile number
        # ============================================
        print("🔍 STEP 2: Looking for mobile number input...")
        
        xpaths_mobile = [
            "//input[@type='tel']",
            "//input[contains(@placeholder, 'mobile')]",
            "//input[contains(@placeholder, 'Mobile')]",
            "//input[@id='mobile']",
            "//input[@name='mobile']",
            "//input[contains(@id, 'phone')]",
            "//input[contains(@id, 'mobile')]",
        ]
        
        mobile_input = None
        for xpath in xpaths_mobile:
            try:
                mobile_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                print(f"✅ Found mobile input using XPath: {xpath}")
                break
            except:
                continue
        
        if mobile_input:
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", mobile_input)
            human_delay(0.2, 0.4)
            
            # Click to focus
            mobile_input.click()
            human_delay(0.1, 0.2)
            
            # Clear existing content
            mobile_input.clear()
            human_delay(0.1, 0.2)
            
            # Type mobile number like human (fast)
            print(f"⌨️ Entering mobile number: {mobile_number}")
            type_like_human(mobile_input, mobile_number)
            print("✅ Mobile number entered!")
            human_delay(0.5, 1)
        else:
            print("⚠️ Mobile input not found")
            driver.save_screenshot(".tmp/mobile_input_not_found.png")
        
        # ============================================
        # STEP 3: Handle Cloudflare checkbox (Conditional)
        # ============================================
        print("🔍 STEP 3: Checking for Cloudflare/verification checkbox...")
        
        checkbox_found = False
        
        # Check for iframe first (Cloudflare often uses iframes)
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"📋 Found {len(iframes)} iframe(s), checking for checkbox...")
                for i, iframe in enumerate(iframes):
                    try:
                        driver.switch_to.frame(iframe)
                        checkbox = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
                        )
                        print(f"✅ Found checkbox in iframe {i}")
                        human_delay(0.5, 1)
                        checkbox.click()
                        print("✅ Cloudflare checkbox clicked!")
                        checkbox_found = True
                        driver.switch_to.default_content()
                        break
                    except:
                        driver.switch_to.default_content()
                        continue
        except Exception as e:
            driver.switch_to.default_content()
        
        # If not in iframe, try main page
        if not checkbox_found:
            try:
                xpaths_checkbox = [
                    "//input[@type='checkbox']",
                    "//span[contains(@class, 'checkbox')]",
                    "//div[contains(@class, 'recaptcha')]",
                    "//div[contains(@class, 'cf-turnstile')]",
                ]
                
                for xpath in xpaths_checkbox:
                    try:
                        checkbox = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        print(f"✅ Found checkbox using XPath: {xpath}")
                        human_delay(0.5, 1)
                        checkbox.click()
                        print("✅ Cloudflare checkbox clicked!")
                        checkbox_found = True
                        break
                    except:
                        continue
            except:
                pass
        
        # Conditional: If checkbox found, clicked. If not, continue.
        if checkbox_found:
            print("✅ Cloudflare handled successfully!")
            human_delay(0.5, 1)
        else:
            print("ℹ️ Cloudflare checkbox not present - continuing to next step...")
        
        # ============================================
        # STEP 4: Find and click Get OTP button
        # ============================================
        print("🔍 STEP 4: Looking for 'Get OTP' button...")
        
        xpaths_otp_button = [
            "//button[contains(text(), 'Get OTP')]",
            "//button[contains(text(), 'GET OTP')]",
            "//button[contains(text(), 'Send OTP')]",
            "//button[@id='get-otp']",
            "//button[contains(@id, 'otp')]",
            "//button[contains(@class, 'otp')]",
            "//button[contains(@class, 'submit')]",
            "//input[@type='submit' and contains(@value, 'OTP')]",
        ]
        
        otp_button = None
        for xpath in xpaths_otp_button:
            try:
                # Wait for button to be present first
                otp_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                print(f"✅ Found 'Get OTP' button using XPath: {xpath}")
                break
            except:
                continue
        
        if otp_button:
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", otp_button)
            human_delay(0.2, 0.4)
            
            # Wait until button is clickable (enabled) - reduced wait time
            print("⏳ Waiting for 'Get OTP' button to be enabled...")
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                print("✅ 'Get OTP' button is now enabled!")
            except:
                print("ℹ️ Button may already be enabled or checking anyway...")
            
            # Click the button
            print("🖱️ Clicking 'Get OTP' button...")
            human_delay(0.2, 0.4)
            ActionChains(driver).move_to_element(otp_button).click().perform()
            print("✅ 'Get OTP' button clicked successfully!")
            human_delay(1, 2)
        else:
            print("⚠️ 'Get OTP' button not found")
            driver.save_screenshot(".tmp/get_otp_not_found.png")
        
        # ============================================
        # STEP 5: Handle Email Screen (Conditional - appears only once)
        # ============================================
        print("\n🔍 STEP 5: Checking for Email screen (one-time occurrence)...")
        
        # Wait for page transition after Get OTP
        print("⏳ Waiting for page transition after OTP request...")
        human_delay(2, 3)
        
        email_screen_found = False
        email_address = "Rahul.hajari@rksv.in"
        
        # Check for email screen label or input field
        xpaths_email_label = [
            "//*[contains(text(), \"What's your email address?\")]",
            "//*[contains(text(), 'email address')]",
            "//label[contains(text(), 'email')]",
        ]
        
        xpaths_email_input = [
            "//input[@placeholder='Enter your email address']",
            "//input[contains(@placeholder, 'email')]",
            "//input[@type='email']",
            "//input[contains(@id, 'email')]",
            "//input[contains(@name, 'email')]",
        ]
        
        # Check if email screen is present
        try:
            email_label = None
            for xpath in xpaths_email_label:
                try:
                    email_label = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    print(f"✅ Found email screen label using XPath: {xpath}")
                    email_screen_found = True
                    break
                except:
                    continue
            
            # Also check for email input field
            email_input = None
            for xpath in xpaths_email_input:
                try:
                    email_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if not email_screen_found:
                        print(f"✅ Found email input field using XPath: {xpath}")
                        email_screen_found = True
                    break
                except:
                    continue
            
            # If email screen found, enter email and click Continue
            if email_screen_found and email_input:
                print("✅ Email screen detected!")
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
                human_delay(0.3, 0.6)
                
                # Click to focus
                email_input.click()
                human_delay(0.2, 0.4)
                
                # Clear existing content
                email_input.clear()
                human_delay(0.1, 0.2)
                
                # Type email address
                print(f"⌨️ Entering email address: {email_address}")
                type_like_human(email_input, email_address)
                print("✅ Email address entered!")
                human_delay(0.5, 1)
                
                # Find and click Continue button
                print("🔍 Looking for Continue button...")
                xpaths_continue_button = [
                    "//button[contains(text(), 'Continue')]",
                    "//button[contains(text(), 'CONTINUE')]",
                    "//button[@type='submit']",
                    "//button[contains(@class, 'continue')]",
                    "//button[contains(@id, 'continue')]",
                ]
                
                continue_button = None
                for xpath in xpaths_continue_button:
                    try:
                        continue_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        print(f"✅ Found Continue button using XPath: {xpath}")
                        break
                    except:
                        continue
                
                if continue_button:
                    # Scroll and click
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                    human_delay(0.3, 0.6)
                    print("🖱️ Clicking Continue button...")
                    ActionChains(driver).move_to_element(continue_button).click().perform()
                    print("✅ Continue button clicked successfully!")
                    human_delay(1, 2)
                else:
                    print("⚠️ Continue button not found")
                    driver.save_screenshot(".tmp/continue_button_not_found.png")
            else:
                print("ℹ️ Email screen not present (already completed) - continuing...")
                
        except Exception as e:
            print(f"ℹ️ Email screen check completed: {e}")
        
        print("\n" + "="*50)
        print("✅ TASK COMPLETE!")
        print("="*50)
        print("📱 Mobile number entered:", mobile_number)
        if otp_button:
            print("🔔 Get OTP button clicked!")
        if email_screen_found:
            print("📧 Email address entered: Rahul.hajari@rksv.in")
        print("📝 Browser will remain open for manual verification.")
        print("🔒 Close the browser manually when done.")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if driver:
            try:
                driver.save_screenshot(".tmp/error_screenshot.png")
                print("📸 Error screenshot saved to .tmp/error_screenshot.png")
            except:
                pass
        sys.exit(1)


if __name__ == "__main__":
    # Execute with default parameters
    open_browser_and_login()
