# SOP: Selenium Browser Automation

> Technical Standard Operating Procedure for browser automation using Selenium

---

## Goal
Automate Chrome browser to open Upstox, click Sign In, enter mobile number, handle Cloudflare (if present), click Get OTP, keep browser open.

## Input
- `url` (str): Target URL to navigate to (default: https://upstox.com/)
- `mobile_number` (str): Mobile number to enter (default: 8976258876)

## Output
- None (side effect: browser opens, navigates, clicks Sign In, enters mobile, handles Cloudflare conditionally, clicks Get OTP, stays open)

## Tool Logic

### Flow
1. Initialize Chrome WebDriver using webdriver-manager (with anti-detection)
2. Navigate to target URL
3. Wait for page to load
4. Find "Sign In" button using XPath
5. Click the Sign In button
6. Wait for login page to load
7. Find mobile number input field (ID or XPath)
8. Enter mobile number with human-like delays
9. **IF Cloudflare checkbox is present:** Click it
10. **ELSE:** Continue to next step
11. Find "Get OTP" button and wait until enabled
12. Click "Get OTP" button
13. Keep browser open (do not close)

### XPath Strategy
- Sign In button: `//a[contains(text(), 'Sign In')]` or `//button[contains(text(), 'Sign In')]`
- Mobile input: `//input[@type='tel']` or `//input[contains(@placeholder, 'mobile')]` or `//input[@id='mobile']`
- Cloudflare checkbox: `//input[@type='checkbox']` or iframe-based challenge
- Get OTP button: `//button[contains(text(), 'Get OTP')]` or `//button[@id='get-otp']` or `//button[contains(@class, 'otp')]`

### Human-Like Behavior
- Add random delays between actions (1-3 seconds)
- Use `ActionChains` for mouse movements
- Scroll into view before clicking
- Clear field before typing
- Type with slight delays between characters
- Wait for button to be enabled before clicking

### Conditional Logic
| Condition | Action |
|-----------|--------|
| Cloudflare checkbox exists | Click it with human-like delay |
| Cloudflare checkbox NOT exists | Skip and continue |
| Get OTP button disabled | Wait until enabled |
| Get OTP button enabled | Click immediately |

### Anti-Detection Measures
- Use undetected-chromedriver or modify navigator.webdriver flag
- Disable automation flags
- Set realistic user-agent and window size
- Handle iframe switches for Cloudflare

### Edge Cases
| Case | Handling |
|------|----------|
| Chrome not installed | Error: Chrome browser required |
| No internet connection | Selenium will timeout on page load |
| WebDriver version mismatch | webdriver-manager handles automatically |
| Sign In button not found | Try multiple XPath strategies |
| Mobile input not found | Try ID, name, type='tel', placeholder |
| Cloudflare blocks automation | Skip if not present, click if present |
| Get OTP button not found | Try text, ID, class-based XPaths |
| Get OTP button disabled | Wait with timeout for it to enable |
| Login page takes time to load | Add explicit wait with longer timeout |

### Dependencies
- `selenium`
- `webdriver-manager`

---

## Revision History
| Date | Author | Change |
|------|--------|--------|
| 2026-02-07 | System Pilot | Initial SOP |
