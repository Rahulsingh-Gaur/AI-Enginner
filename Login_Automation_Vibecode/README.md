# Web Automation Framework with Playwright

A robust, scalable web automation framework built with Playwright and pytest following the Page Object Model (POM) pattern.

## Features

- **Page Object Model (POM)** pattern for maintainable tests
- **Playwright** for reliable browser automation
- **pytest** for test execution and reporting
- **Configurable** via environment variables
- **Screenshot capture** on test failure
- **Logging** with both console and file output
- **Wait utilities** for handling dynamic elements
- **Cross-browser support** (Chromium, Firefox, WebKit)

## Project Structure

```
Login_Automation_Vibecode/
├── config/                 # Configuration files
│   ├── settings.py         # Main settings class
│   └── .env.example        # Environment variables template
├── pages/                  # Page Object classes
│   └── base_page.py        # Base page with common methods
├── tests/                  # Test files
│   ├── conftest.py         # Pytest fixtures and hooks
│   └── test_example.py     # Example test file
├── utils/                  # Utility modules
│   ├── logger.py           # Logging utility
│   └── wait_utils.py       # Wait helper methods
├── reports/                # Test reports (generated)
├── screenshots/            # Screenshots (generated)
├── logs/                   # Log files (generated)
├── venv/                   # Virtual environment
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

### 1. Create Virtual Environment (if not already created)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Configure Environment Variables

```bash
cp config/.env.example .env
# Edit .env with your actual values
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with specific browser
```bash
pytest --browser=chromium
pytest --browser=firefox
```

### Run in headless mode
```bash
pytest --headless
```

### Run with specific base URL
```bash
pytest --base-url=https://your-app.com
```

### Run with markers
```bash
pytest -m smoke
pytest -m "not slow"
```

### Run in parallel
```bash
pytest -n auto
```

### Generate HTML report
```bash
pytest --html=reports/report.html
```

### View Auto-Generated Reports
After test execution, the following reports are automatically generated in `reports/`:

| Report | Description |
|--------|-------------|
| `TestExecutionReport_{timestamp}.md` | Markdown report with full test details |
| `TestExecutionReport_{timestamp}.html` | Interactive HTML dashboard |
| `test_report_{timestamp}.json` | Machine-readable JSON for CI/CD |
| `BugReport.md` | Jira-formatted bug report (failed tests only) |

### Screenshots on Failure
Screenshots are automatically captured when tests fail:
- Location: `screenshots/`
- Naming: `FAILED_{test_name}_{timestamp}.png`
- Configurable via `SCREENSHOT_ON_FAILURE` env variable

## Creating New Tests

### 1. Create a Page Object

Create a new file in `pages/` for your page:

```python
# pages/login_page.py
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Selectors
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = ".error-message"
    
    def login(self, username: str, password: str):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return self
    
    def is_error_visible(self) -> bool:
        return self.is_element_visible(self.ERROR_MESSAGE)
```

### 2. Create Test File

Create a new test file in `tests/`:

```python
# tests/test_login.py
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from config.settings import settings

class TestLogin:
    def test_successful_login(self, page: Page, base_url: str):
        login_page = LoginPage(page)
        login_page.navigate_to(f"{base_url}/login")
        login_page.login(settings.USERNAME, settings.PASSWORD)
        login_page.assert_url_contains("/dashboard")
    
    def test_invalid_login(self, page: Page, base_url: str):
        login_page = LoginPage(page)
        login_page.navigate_to(f"{base_url}/login")
        login_page.login("invalid", "invalid")
        assert login_page.is_error_visible()
```

## Configuration

All configuration is managed through environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Application base URL | https://example.com |
| `BROWSER` | Browser to use (chromium/firefox/webkit) | chromium |
| `HEADLESS` | Run in headless mode (true/false) | false |
| `SLOW_MO` | Slow motion delay in ms | 0 |
| `USERNAME` | Test username | - |
| `PASSWORD` | Test password | - |
| `DEFAULT_TIMEOUT` | Default timeout in ms | 30000 |
| `SCREENSHOT_ON_FAILURE` | Capture screenshot on failure (true/false) | true |

## Utilities

### Logger

```python
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Information message")
logger.error("Error message")
```

### Wait Utils

```python
from pages.base_page import BasePage

base_page = BasePage(page)
base_page.wait_for_selector("#element")
base_page.wait_for_text("Success")
base_page.wait_for_page_load()
```

## Best Practices

1. **Use Page Objects**: Keep test logic separate from page interactions
2. **Descriptive Selectors**: Use data-testid or meaningful class names
3. **Explicit Waits**: Always wait for elements before interacting
4. **Independent Tests**: Each test should be able to run independently
5. **Meaningful Names**: Use descriptive test and method names
6. **Docstrings**: Document what each test verifies
7. **Screenshots**: Enable screenshot on failure for debugging

## Bug Report Format

The `BugReport.md` file is auto-generated in Jira format for easy bug ticket creation:

```jira
h1. Test Case Name

h2. Summary
Test case failed during automated execution

h2. Environment
| Browser | chromium |
| Base URL | https://your-app.com |

h2. Steps to Reproduce
# Step 1
# Step 2

h2. Expected Result
Test should pass

h2. Actual Result
Test failed with error

h2. Error Details
Error message and stack trace

h2. Attachments
* Screenshot: [path/to/screenshot.png]

h2. Labels
automated-test, chromium, regression, bug
```

## Troubleshooting

### Browser not found
```bash
playwright install chromium
```

### Permission issues on macOS
```bash
xattr -cr venv/
```

### Tests timing out
Increase timeout in `.env`:
```
DEFAULT_TIMEOUT=60000
```
