"""
Example test file demonstrating the framework usage.
This is a template - replace with actual tests for your application.
"""
import pytest
from playwright.sync_api import Page

from pages.base_page import BasePage
from config.settings import settings


class TestExample:
    """Example test class demonstrating framework capabilities."""
    
    def test_page_navigation(self, page: Page, app_base_url: str):
        """
        Example test demonstrating basic navigation.
        
        Steps:
        1. Navigate to base URL
        2. Verify page loaded
        """
        base_page = BasePage(page)
        base_page.navigate_to(app_base_url)
        
        # Wait for page to load
        assert base_page.wait_for_page_load(), "Page did not load"
        
        # Take screenshot
        base_page.take_screenshot("navigation_test")
    
    @pytest.mark.smoke
    def test_page_title(self, page: Page, app_base_url: str):
        """
        Example smoke test verifying page title.
        
        Steps:
        1. Navigate to base URL
        2. Verify page has a title
        """
        base_page = BasePage(page)
        base_page.navigate_to(app_base_url)
        
        # Get and verify page title
        title = base_page.get_page_title()
        assert title, "Page title is empty"
        print(f"Page title: {title}")
    
    @pytest.mark.skip(reason="Template test - implement with actual selectors")
    def test_login_functionality(self, page: Page, app_base_url: str):
        """
        Example login test (template - implement with actual selectors).
        
        Steps:
        1. Navigate to login page
        2. Fill in username
        3. Fill in password
        4. Click login button
        5. Verify successful login
        """
        base_page = BasePage(page)
        base_page.navigate_to(f"{app_base_url}/login")
        
        # Example login steps (replace with actual selectors)
        # base_page.fill("#username", settings.USERNAME)
        # base_page.fill("#password", settings.PASSWORD)
        # base_page.click("#login-button")
        
        # Verify login success
        # base_page.assert_url_contains("/dashboard")
        pass


class TestWithBasePage:
    """Example tests using BasePage class methods."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, app_base_url: str):
        """Setup fixture for each test."""
        self.page = BasePage(page)
        self.base_url = app_base_url
        self.page.navigate_to(app_base_url)
    
    def test_basic_interactions(self):
        """Test basic page interactions."""
        # Example interactions (replace with actual selectors)
        # self.page.click("#some-button")
        # self.page.fill("#some-input", "test text")
        # self.page.assert_element_visible("#some-element")
        pass
