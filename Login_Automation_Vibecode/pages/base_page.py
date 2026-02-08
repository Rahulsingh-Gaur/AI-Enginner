"""
Base Page class for the Page Object Model pattern.
All page classes should inherit from this class.
"""
from playwright.sync_api import Page, Locator
from typing import Optional
import logging
import os
from pathlib import Path
from datetime import datetime

from utils.wait_utils import WaitUtils
from config.settings import settings

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all page objects.
    Provides common methods for page interactions.
    """
    
    def __init__(self, page: Page):
        """
        Initialize the BasePage with a Playwright page instance.
        
        Args:
            page: The Playwright page instance.
        """
        self.page = page
        self.wait_utils = WaitUtils(page, settings.DEFAULT_TIMEOUT)
        self.logger = logger
    
    # ==================== Navigation ====================
    
    def navigate_to(self, url: str) -> "BasePage":
        """
        Navigate to a specific URL.
        
        Args:
            url: The URL to navigate to.
            
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info(f"Navigating to: {url}")
        self.page.goto(url)
        return self
    
    def get_current_url(self) -> str:
        """
        Get the current page URL.
        
        Returns:
            The current URL.
        """
        return self.page.url
    
    def get_page_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            The page title.
        """
        return self.page.title()
    
    def reload_page(self) -> "BasePage":
        """
        Reload the current page.
        
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info("Reloading page")
        self.page.reload()
        return self
    
    def go_back(self) -> "BasePage":
        """
        Go back to the previous page.
        
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info("Going back")
        self.page.go_back()
        return self
    
    # ==================== Element Actions ====================
    
    def click(self, selector: str) -> "BasePage":
        """
        Click on an element.
        
        Args:
            selector: The CSS or XPath selector.
            
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info(f"Clicking on: {selector}")
        self.page.click(selector)
        return self
    
    def fill(self, selector: str, text: str) -> "BasePage":
        """
        Fill a text input field.
        
        Args:
            selector: The CSS or XPath selector.
            text: The text to fill in.
            
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info(f"Filling {selector} with: {text}")
        self.page.fill(selector, text)
        return self
    
    def clear_and_fill(self, selector: str, text: str) -> "BasePage":
        """
        Clear the field and then fill it with text.
        
        Args:
            selector: The CSS or XPath selector.
            text: The text to fill in.
            
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info(f"Clearing and filling {selector} with: {text}")
        self.page.fill(selector, "")
        self.page.fill(selector, text)
        return self
    
    def get_text(self, selector: str) -> str:
        """
        Get text content of an element.
        
        Args:
            selector: The CSS or XPath selector.
            
        Returns:
            The text content of the element.
        """
        return self.page.inner_text(selector)
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get an attribute value of an element.
        
        Args:
            selector: The CSS or XPath selector.
            attribute: The attribute name.
            
        Returns:
            The attribute value or None if not found.
        """
        return self.page.get_attribute(selector, attribute)
    
    def is_element_visible(self, selector: str) -> bool:
        """
        Check if an element is visible.
        
        Args:
            selector: The CSS or XPath selector.
            
        Returns:
            True if visible, False otherwise.
        """
        return self.page.is_visible(selector)
    
    def is_element_enabled(self, selector: str) -> bool:
        """
        Check if an element is enabled.
        
        Args:
            selector: The CSS or XPath selector.
            
        Returns:
            True if enabled, False otherwise.
        """
        return self.page.is_enabled(selector)
    
    def select_option(self, selector: str, value: str) -> "BasePage":
        """
        Select an option from a dropdown.
        
        Args:
            selector: The CSS or XPath selector for the select element.
            value: The option value to select.
            
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info(f"Selecting option '{value}' from {selector}")
        self.page.select_option(selector, value)
        return self
    
    def hover(self, selector: str) -> "BasePage":
        """
        Hover over an element.
        
        Args:
            selector: The CSS or XPath selector.
            
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info(f"Hovering over: {selector}")
        self.page.hover(selector)
        return self
    
    # ==================== Wait Methods ====================
    
    def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to appear in the DOM.
        
        Args:
            selector: The CSS or XPath selector.
            timeout: Timeout in milliseconds.
            
        Returns:
            True if element found, False otherwise.
        """
        return self.wait_utils.wait_for_element_visible(selector, timeout)
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for the page to fully load.
        
        Args:
            timeout: Timeout in milliseconds.
            
        Returns:
            True if page loaded, False otherwise.
        """
        return self.wait_utils.wait_for_page_load(timeout)
    
    def wait_for_text(self, text: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for specific text to appear on the page.
        
        Args:
            text: The text to wait for.
            timeout: Timeout in milliseconds.
            
        Returns:
            True if text found, False otherwise.
        """
        return self.wait_utils.wait_for_text_visible(text, timeout=timeout)
    
    # ==================== Screenshot ====================
    
    def take_screenshot(self, name: Optional[str] = None) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            name: The screenshot file name. If None, a timestamp will be used.
            
        Returns:
            The path to the saved screenshot.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name or 'screenshot'}_{timestamp}.png"
        
        screenshot_dir = Path(settings.SCREENSHOT_DIR)
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        screenshot_path = screenshot_dir / filename
        self.page.screenshot(path=str(screenshot_path), full_page=True)
        
        self.logger.info(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)
    
    # ==================== JavaScript Execution ====================
    
    def execute_js(self, script: str, *args):
        """
        Execute JavaScript on the page.
        
        Args:
            script: The JavaScript code to execute.
            *args: Arguments to pass to the script.
            
        Returns:
            The result of the JavaScript execution.
        """
        return self.page.evaluate(script, *args)
    
    def scroll_to_element(self, selector: str) -> "BasePage":
        """
        Scroll to an element.
        
        Args:
            selector: The CSS or XPath selector.
            
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info(f"Scrolling to: {selector}")
        element = self.page.locator(selector)
        element.scroll_into_view_if_needed()
        return self
    
    def scroll_to_bottom(self) -> "BasePage":
        """
        Scroll to the bottom of the page.
        
        Returns:
            The current page instance for method chaining.
        """
        self.logger.info("Scrolling to bottom of page")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        return self
    
    # ==================== Assertions ====================
    
    def assert_url_contains(self, text: str) -> bool:
        """
        Assert that the current URL contains specific text.
        
        Args:
            text: The text to check for in the URL.
            
        Returns:
            True if URL contains the text.
        """
        current_url = self.get_current_url()
        assert text in current_url, f"URL '{current_url}' does not contain '{text}'"
        return True
    
    def assert_title_contains(self, text: str) -> bool:
        """
        Assert that the page title contains specific text.
        
        Args:
            text: The text to check for in the title.
            
        Returns:
            True if title contains the text.
        """
        title = self.get_page_title()
        assert text in title, f"Title '{title}' does not contain '{text}'"
        return True
    
    def assert_element_visible(self, selector: str) -> bool:
        """
        Assert that an element is visible.
        
        Args:
            selector: The CSS or XPath selector.
            
        Returns:
            True if element is visible.
        """
        assert self.is_element_visible(selector), f"Element {selector} is not visible"
        return True
    
    def assert_text_visible(self, text: str) -> bool:
        """
        Assert that specific text is visible on the page.
        
        Args:
            text: The text to check for.
            
        Returns:
            True if text is visible.
        """
        is_visible = self.page.locator(f"text={text}").is_visible()
        assert is_visible, f"Text '{text}' is not visible on the page"
        return True
