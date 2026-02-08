"""
Sample test to demonstrate Bug Report generation.
This test is designed to fail to show the bug report format.
"""
import pytest
from playwright.sync_api import Page

from pages.base_page import BasePage


class TestSampleFailures:
    """Sample tests to demonstrate bug report generation."""
    
    @pytest.mark.skip(reason="Demo test - enable to see bug report generation")
    def test_intentional_failure(self, page: Page, app_base_url: str):
        """
        This test is designed to fail to demonstrate bug reporting.
        
        Steps:
        1. Navigate to base URL
        2. Try to click on non-existent element
        3. This will fail and generate a bug report entry
        """
        base_page = BasePage(page)
        base_page.navigate_to(app_base_url)
        
        # This will fail - element doesn't exist
        base_page.click("#non-existent-element-for-demo")
    
    @pytest.mark.skip(reason="Demo test - enable to see bug report generation")
    def test_assertion_failure(self, page: Page, app_base_url: str):
        """
        This test demonstrates assertion failure in bug report.
        
        Steps:
        1. Navigate to base URL
        2. Assert title contains expected text
        3. This will likely fail on example.com
        """
        base_page = BasePage(page)
        base_page.navigate_to(app_base_url)
        
        # This assertion will likely fail
        base_page.assert_title_contains("Expected Title That Doesn't Exist")
