# Web Automation Framework - Team Guide

A comprehensive guide for setting up and using the Playwright-based Web Automation Framework.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Framework Setup](#framework-setup)
4. [Creating Test Cases](#creating-test-cases)
5. [Running Tests](#running-tests)
6. [Understanding Reports](#understanding-reports)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Download Link |
|----------|---------|---------------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| Git | Latest | https://git-scm.com/downloads |
| VS Code (Recommended) | Latest | https://code.visualstudio.com/ |

### VS Code Extensions (Recommended)

- Python (Microsoft)
- Pylance
- Markdown Preview Enhanced

---

## Quick Start

### Step 1: Clone the Repository

```bash
git clone git@github.com:Rahulsingh-Gaur/AI-Enginner.git
cd AI-Enginner/Login_Automation_Vibecode
```

### Step 2: Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 4: Configure Environment

```bash
cp config/.env.example .env
```

Edit `.env` file with your test data:
```env
BASE_URL=https://your-app.com/login
USERNAME=your_username
PASSWORD=your_password
```

### Step 5: Run Sample Test

```bash
pytest tests/test_example.py -v --headed
```

✅ **Success!** You should see a browser open and run the test.

---

## Framework Setup

### Project Structure

```
Login_Automation_Vibecode/
├── config/                 # Configuration files
│   ├── settings.py         # Main settings
│   └── .env.example        # Environment template
├── pages/                  # Page Object Models
│   ├── base_page.py        # Base class with common methods
│   └── login_page.py       # Login page specific methods
├── tests/                  # Test files
│   ├── conftest.py         # Pytest fixtures
│   ├── test_login.py       # Login test cases
│   └── test_example.py     # Example tests
├── utils/                  # Utilities
│   ├── logger.py           # Logging utility
│   ├── report_generator.py # Report generation
│   └── wait_utils.py       # Wait helpers
├── reports/                # Auto-generated reports
├── screenshots/            # Auto-captured screenshots
└── logs/                   # Execution logs
```

### Key Concepts

#### 1. Page Object Model (POM)
Each web page has a corresponding Python class:
- **Selectors**: Define UI elements (buttons, fields, etc.)
- **Actions**: Methods to interact with elements
- **Verifications**: Methods to check page state

#### 2. Test Structure
Each test follows this pattern:
```python
def test_feature_name(self):
    """
    Test Description
    
    Steps:
    1. Step one
    2. Step two
    Expected Result: What should happen
    """
    # Test code here
    assert actual == expected, "Error message if failed"
```

---

## Creating Test Cases

### Step-by-Step Guide

#### Step 1: Identify the Page

Determine which page you're testing (e.g., Login, Dashboard, Profile).

#### Step 2: Create/Update Page Object

If testing a new page, create a file in `pages/`:

```python
# pages/dashboard_page.py
from pages.base_page import BasePage

class DashboardPage(BasePage):
    """Page Object for Dashboard Page"""
    
    # Selectors
    WELCOME_MESSAGE = ".welcome-msg"
    LOGOUT_BUTTON = "#logout-btn"
    PROFILE_LINK = "#profile-link"
    
    def __init__(self, page, base_url):
        super().__init__(page)
        self.base_url = base_url
    
    def navigate_to_dashboard(self):
        """Navigate to dashboard"""
        self.navigate_to(f"{self.base_url}/dashboard")
        return self
    
    def click_logout(self):
        """Click logout button"""
        self.click(self.LOGOUT_BUTTON)
        return self
    
    def get_welcome_text(self):
        """Get welcome message text"""
        return self.get_text(self.WELCOME_MESSAGE)
    
    def is_on_dashboard(self):
        """Check if on dashboard page"""
        return self.is_element_visible(self.WELCOME_MESSAGE)
```

#### Step 3: Create Test File

Create a test file in `tests/`:

```python
# tests/test_dashboard.py
import pytest
from playwright.sync_api import Page
from pages.dashboard_page import DashboardPage

class TestDashboard:
    """Test cases for Dashboard functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, app_base_url: str):
        """Setup: Navigate to dashboard before each test"""
        self.dashboard = DashboardPage(page, app_base_url)
        self.dashboard.navigate_to_dashboard()
    
    def test_dashboard_loads_successfully(self):
        """
        TC_DASH_001: Verify dashboard loads
        
        Steps:
        1. Navigate to dashboard
        Expected Result: Dashboard page loads with welcome message
        """
        # Verify dashboard loaded
        assert self.dashboard.is_on_dashboard(), \
            "Dashboard should be visible"
        
        # Verify welcome message
        welcome_text = self.dashboard.get_welcome_text()
        assert "Welcome" in welcome_text, \
            f"Welcome message should contain 'Welcome', got: {welcome_text}"
    
    def test_logout_functionality(self):
        """
        TC_DASH_002: Verify logout works
        
        Steps:
        1. Click logout button
        Expected Result: User redirected to login page
        """
        # Click logout
        self.dashboard.click_logout()
        
        # Verify redirected to login
        assert "login" in self.dashboard.get_current_url(), \
            "Should redirect to login page after logout"
```

#### Step 4: Add Test Data

Add test data at the top of your test file:

```python
# Test Data
VALID_USERNAME = "testuser"
VALID_PASSWORD = "TestPass123"
INVALID_USERNAME = "wronguser"
INVALID_PASSWORD = "wrongpass"
```

#### Step 5: Mark Test Priority

Use pytest markers for categorization:

```python
@pytest.mark.critical    # Critical priority
@pytest.mark.high        # High priority
@pytest.mark.medium      # Medium priority
@pytest.mark.low         # Low priority
@pytest.mark.smoke       # Smoke test
@pytest.mark.regression  # Regression test
```

---

## Test Case Samples

### Sample 1: Login with Valid Credentials

```python
@pytest.mark.critical
@pytest.mark.smoke
def test_login_with_valid_credentials(self):
    """
    TC_LOGIN_001: Verify login with valid credentials
    
    Steps:
    1. Enter valid username
    2. Enter valid password
    3. Click Sign in button
    Expected Result: User logged in and redirected to dashboard
    """
    # Arrange
    login_page = LoginPage(self.page, self.base_url)
    login_page.navigate_to_login()
    
    # Act
    login_page.enter_username(VALID_USERNAME)
    login_page.enter_password(VALID_PASSWORD)
    login_page.click_sign_in()
    
    # Assert
    assert login_page.is_on_dashboard(), \
        "Expected: User should be on dashboard after login"
```

### Sample 2: Login with Invalid Credentials

```python
@pytest.mark.critical
def test_login_with_invalid_credentials(self):
    """
    TC_LOGIN_002: Verify login fails with invalid credentials
    
    Steps:
    1. Enter invalid username
    2. Enter invalid password
    3. Click Sign in button
    Expected Result: Error message shown, stay on login page
    """
    # Arrange
    login_page = LoginPage(self.page, self.base_url)
    login_page.navigate_to_login()
    
    # Act
    login_page.enter_username(INVALID_USERNAME)
    login_page.enter_password(INVALID_PASSWORD)
    login_page.click_sign_in()
    
    # Assert
    assert login_page.is_on_login_page(), \
        "Expected: User should stay on login page"
    assert login_page.is_error_message_visible(), \
        "Expected: Error message should be displayed"
```

### Sample 3: Field Validation

```python
@pytest.mark.high
def test_empty_username_validation(self):
    """
    TC_LOGIN_003: Verify validation for empty username
    
    Steps:
    1. Leave username empty
    2. Enter valid password
    3. Click Sign in
    Expected Result: Error message: "Username is required"
    """
    login_page = LoginPage(self.page, self.base_url)
    login_page.navigate_to_login()
    
    login_page.enter_username("")
    login_page.enter_password(VALID_PASSWORD)
    login_page.click_sign_in()
    
    error_msg = login_page.get_error_message()
    assert "username" in error_msg.lower(), \
        f"Expected error about username, got: {error_msg}"
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_login.py

# Run specific test
pytest tests/test_login.py::TestLoginFunctionality::test_tc_login_001

# Run with browser visible (headed mode)
pytest --headed

# Run in headless mode (faster)
pytest --headless
```

### Run by Priority

```bash
# Run only critical tests
pytest -m critical

# Run high and critical tests
pytest -m "high or critical"

# Run smoke tests
pytest -m smoke

# Exclude slow tests
pytest -m "not slow"
```

### Run with Reporting

```bash
# Run and generate all reports
pytest -v

# Reports will be auto-generated in reports/ folder:
# - TestExecutionReport_{timestamp}.md
# - TestExecutionReport_{timestamp}.html
# - BugReport.md
```

---

## Understanding Reports

### Test Execution Report

**Location:** `reports/TestExecutionReport_{timestamp}.md`

**Contains:**
- Summary (Total, Passed, Failed, Skipped)
- Failed test details with error messages
- Passed test list
- Screenshots for failed tests

**Example:**
```
## Summary
| Status | Count |
|--------|-------|
| ✅ Passed | 15 |
| ❌ Failed | 2 |
| ⚠️ Skipped | 1 |

## Failed Tests
### test_login_with_invalid_credentials
Error: BUG: Login succeeded with invalid password
Screenshot: screenshots/FAILED_...png
```

### Bug Report

**Location:** `reports/BugReport.md`

**Contains:**
- Table of all failed tests
- Expected vs Actual comparison
- Steps to reproduce
- Screenshot references

### Screenshots

**Location:** `screenshots/`

- Auto-captured when tests fail
- Naming: `FAILED_{test_name}_{timestamp}.png`

---

## Best Practices

### 1. Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Test files | `test_*.py` | `test_login.py` |
| Test classes | `Test*` | `TestLoginFunctionality` |
| Test methods | `test_*` | `test_valid_login` |
| Page objects | `*Page` | `LoginPage` |
| Selectors | UPPERCASE | `USERNAME_INPUT` |

### 2. Test Documentation

Always include docstrings:
```python
def test_feature(self):
    """
    TC_ID: Short description
    
    Preconditions: What needs to be set up
    Steps:
    1. Step one
    2. Step two
    Expected Result: What should happen
    """
```

### 3. Assertions

Always use descriptive error messages:
```python
# Good
assert login_page.is_on_dashboard(), \
    "Expected: User should be on dashboard after valid login"

# Bad
assert login_page.is_on_dashboard()
```

### 4. Selectors

Use stable selectors (avoid dynamic IDs):
```python
# Good (data-testid)
USERNAME_INPUT = "[data-testid='username']"

# Good (ID)
USERNAME_INPUT = "#username"

# Bad (dynamic class)
USERNAME_INPUT = ".form-control:nth-child(1)"
```

### 5. Wait Strategy

Always wait for elements before interacting:
```python
# Wait then interact
login_page.wait_for_selector(login_page.USERNAME_INPUT)
login_page.enter_username("test")

# Or use built-in waits
login_page.wait_for_page_load()
```

---

## Troubleshooting

### Issue 1: Virtual Environment Not Activating

**Symptom:** `source venv/bin/activate` fails

**Solution:**
```bash
# Check if venv exists
ls -la venv/

# If not, create it
python3 -m venv venv
source venv/bin/activate
```

### Issue 2: Playwright Browser Not Found

**Symptom:** `Executable doesn't exist` error

**Solution:**
```bash
playwright install chromium
```

### Issue 3: Tests Not Collecting

**Symptom:** `collected 0 items`

**Solution:**
- Check test file names start with `test_`
- Check test functions start with `test_`
- Check class names start with `Test`

### Issue 4: Import Errors

**Symptom:** `ModuleNotFoundError`

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue 5: Selectors Not Working

**Symptom:** Element not found errors

**Solution:**
1. Check selector in browser DevTools
2. Wait for element to be visible
3. Check if element is in iframe
4. Verify page fully loaded

---

## Checklist for New Test Cases

Before submitting test cases, verify:

- [ ] Test file named correctly (`test_*.py`)
- [ ] Test class named correctly (`Test*`)
- [ ] Test method named correctly (`test_*`)
- [ ] Docstring includes TC_ID, Steps, Expected Result
- [ ] Appropriate priority marker added (`@pytest.mark.critical/high/medium/low`)
- [ ] Selectors are stable (not dynamic)
- [ ] Error messages are descriptive
- [ ] Test runs successfully locally
- [ ] Screenshots captured for failures

---

## Team Contacts

| Role | Name | Contact |
|------|------|---------|
| Automation Lead | - | - |
| QA Manager | - | - |
| Developer | - | - |

---

## Additional Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Page Object Model Guide](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)

---

**Happy Testing! 🚀**

*Last Updated: 2026-02-08*
