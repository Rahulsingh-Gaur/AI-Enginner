# Findings

> Research, discoveries, and constraints log

---

## Discovery Phase

**Date:** 2026-02-07

### Answers to Discovery Questions

| Question | Answer |
|----------|--------|
| **North Star** | Generate Web automation using Selenium: Open Chrome → Navigate to https://upstox.com/ → Wait 10 seconds → Close browser |
| **Integrations** | None |
| **Source of Truth** | None |
| **Delivery Payload** | None (local execution) |
| **Behavioral Rules** | None |

---

## Research

### Selenium WebDriver Best Practices

1. **ChromeDriver Requirements:**
   - Requires Chrome browser installed
   - ChromeDriver version must match Chrome browser version
   - Can use `webdriver-manager` for automatic driver management

2. **Key Components:**
   - `webdriver.Chrome()` - Initialize Chrome browser
   - `driver.get(url)` - Navigate to URL
   - `time.sleep(seconds)` - Wait/sleep
   - `driver.quit()` - Close browser and cleanup

3. **XPath Strategies for Finding Elements:**
   - `//button[contains(text(), 'Sign In')]` - Text contains
   - `//a[contains(text(), 'Sign In')]` - Link text
   - `//button[contains(@class, 'signin')]` - Class contains
   - `//a[contains(@href, 'login')]` - Href contains
   - `WebDriverWait` with `EC.element_to_be_clickable()` - Explicit wait

4. **Keep Browser Open:**
   - Use `options.add_experimental_option("detach", True)`
   - Do not call `driver.quit()`

5. **Recommended Python Package:**
   - `selenium` - Core WebDriver library
   - `webdriver-manager` - Automatic ChromeDriver management (optional but recommended)

---

## Constraints

*Technical and business constraints to be noted*
