---
name: code-reviewer
description: Review and validate Python and Selenium automation code for correctness, best practices, performance, and maintainability. Use when user asks to check, review, validate, audit, or improve Python/Selenium code, identify bugs, optimize scripts, follow coding standards, or ensure code quality in automation projects.
---

# Code Reviewer - Python & Selenium

Review Python and Selenium automation code for quality, correctness, and best practices.

## When to Use

- Review Python automation scripts
- Check Selenium web automation code
- Identify bugs or anti-patterns
- Optimize code performance
- Validate error handling
- Ensure coding standards compliance
- Check code maintainability

## Review Checklist

### Python Best Practices
- [ ] PEP 8 compliance (naming, spacing, imports)
- [ ] Docstrings for functions and modules
- [ ] Type hints where appropriate
- [ ] No hardcoded credentials or sensitive data
- [ ] Proper file/path handling
- [ ] Virtual environment usage mentioned

### Selenium Specific
- [ ] Uses `webdriver_manager` for driver management
- [ ] Proper ChromeOptions configuration
- [ ] Anti-detection measures if needed
- [ ] Robust XPath/CSS selectors (multiple fallbacks)
- [ ] Explicit waits instead of `time.sleep()`
- [ ] Proper error handling with try-except
- [ ] Screenshots on failure
- [ ] Driver cleanup (quit() in finally block)

### Code Quality
- [ ] Functions are modular and reusable
- [ ] No code duplication (DRY principle)
- [ ] Meaningful variable names
- [ ] Constants defined at module level
- [ ] Configuration externalized (not hardcoded)

### Performance
- [ ] Efficient selectors (prefer ID over XPath)
- [ ] Minimal implicit waits
- [ ] No unnecessary browser operations
- [ ] Batch operations where possible

### Security
- [ ] No hardcoded passwords/keys
- [ ] Sensitive data in environment variables
- [ ] Input validation present

## Review Process

1. **Read the code file(s)** requested by user
2. **Check against checklist** above
3. **Identify issues** with line numbers and severity
4. **Suggest fixes** with code examples
5. **Provide summary** of findings

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| 🔴 **Critical** | Code will fail or cause errors | Must fix |
| 🟠 **High** | Serious anti-pattern or bug | Should fix |
| 🟡 **Medium** | Code works but suboptimal | Recommend fix |
| 🟢 **Low** | Style/nitpick | Optional fix |

## Output Format

```markdown
## Code Review Report

### Summary
- **File**: `filename.py`
- **Lines of Code**: X
- **Issues Found**: X (🔴 X, 🟠 X, 🟡 X, 🟢 X)
- **Overall Rating**: ⭐⭐⭐⭐⭐ (Excellent/Good/Needs Work/Poor)

### Issues

#### 🔴 Critical (X)
| Line | Issue | Fix |
|------|-------|-----|
| 15 | Missing driver.quit() | Add finally block |

#### 🟠 High (X)
| Line | Issue | Fix |
|------|-------|-----|
| 23 | Hardcoded XPath | Add fallback selectors |

#### 🟡 Medium (X)
| Line | Issue | Fix |
|------|-------|-----|
| 45 | time.sleep(10) | Use WebDriverWait |

#### 🟢 Low (X)
| Line | Issue | Fix |
|------|-------|-----|
| 12 | Variable name 'x' | Use descriptive name |

### Recommendations
1. ...
2. ...

### Improved Code
```python
# Show key improvements
```
```

## Common Issues & Fixes

### Issue: Hardcoded time.sleep()
```python
# Bad
time.sleep(5)

# Good
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button"))
)
```

### Issue: Single XPath selector
```python
# Bad
element = driver.find_element(By.XPATH, "//button[@class='btn-123']")

# Good
xpaths = [
    "//button[contains(text(), 'Submit')]",
    "//button[@id='submit']",
    "//input[@type='submit']",
]
for xpath in xpaths:
    try:
        element = driver.find_element(By.XPATH, xpath)
        break
    except NoSuchElementException:
        continue
```

### Issue: No error handling
```python
# Bad
driver.get(url)
button.click()

# Good
try:
    driver.get(url)
    button.click()
except Exception as e:
    driver.save_screenshot("error.png")
    print(f"Error: {e}")
    raise
```

### Issue: Missing driver cleanup
```python
# Bad
driver = webdriver.Chrome()
driver.get(url)
# No quit!

# Good
driver = None
try:
    driver = webdriver.Chrome()
    driver.get(url)
    # ... operations ...
finally:
    if driver:
        driver.quit()
```
