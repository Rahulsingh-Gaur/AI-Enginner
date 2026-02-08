"""
Wait utilities for the automation framework.
Provides helper methods for waiting on various conditions.
"""
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WaitUtils:
    """Utility class for waiting operations."""
    
    def __init__(self, page: Page, default_timeout: int = 30000):
        """
        Initialize WaitUtils with a page instance.
        
        Args:
            page: The Playwright page instance.
            default_timeout: Default timeout in milliseconds.
        """
        self.page = page
        self.default_timeout = default_timeout
    
    def wait_for_element_visible(
        self, 
        selector: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for an element to be visible.
        
        Args:
            selector: The CSS or XPath selector.
            timeout: Timeout in milliseconds.
            
        Returns:
            True if element is visible, False otherwise.
        """
        try:
            self.page.wait_for_selector(
                selector, 
                state="visible", 
                timeout=timeout or self.default_timeout
            )
            return True
        except PlaywrightTimeoutError:
            logger.error(f"Element not visible: {selector}")
            return False
    
    def wait_for_element_hidden(
        self, 
        selector: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for an element to be hidden.
        
        Args:
            selector: The CSS or XPath selector.
            timeout: Timeout in milliseconds.
            
        Returns:
            True if element is hidden, False otherwise.
        """
        try:
            self.page.wait_for_selector(
                selector, 
                state="hidden", 
                timeout=timeout or self.default_timeout
            )
            return True
        except PlaywrightTimeoutError:
            logger.error(f"Element still visible: {selector}")
            return False
    
    def wait_for_element_enabled(
        self, 
        selector: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for an element to be enabled.
        
        Args:
            selector: The CSS or XPath selector.
            timeout: Timeout in milliseconds.
            
        Returns:
            True if element is enabled, False otherwise.
        """
        try:
            self.page.wait_for_function(
                f"document.querySelector('{selector}') && !document.querySelector('{selector}').disabled",
                timeout=timeout or self.default_timeout
            )
            return True
        except PlaywrightTimeoutError:
            logger.error(f"Element not enabled: {selector}")
            return False
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for the page to fully load.
        
        Args:
            timeout: Timeout in milliseconds.
            
        Returns:
            True if page loaded, False otherwise.
        """
        try:
            self.page.wait_for_load_state(
                "networkidle", 
                timeout=timeout or self.default_timeout
            )
            return True
        except PlaywrightTimeoutError:
            logger.error("Page did not load within timeout")
            return False
    
    def wait_for_url_contains(
        self, 
        url_part: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for URL to contain specific text.
        
        Args:
            url_part: The URL substring to wait for.
            timeout: Timeout in milliseconds.
            
        Returns:
            True if URL contains the text, False otherwise.
        """
        try:
            self.page.wait_for_url(
                f"**/*{url_part}*", 
                timeout=timeout or self.default_timeout
            )
            return True
        except PlaywrightTimeoutError:
            logger.error(f"URL does not contain: {url_part}")
            return False
    
    def wait_for_text_visible(
        self, 
        text: str, 
        selector: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for specific text to be visible on the page.
        
        Args:
            text: The text to wait for.
            selector: Optional selector to scope the search.
            timeout: Timeout in milliseconds.
            
        Returns:
            True if text is visible, False otherwise.
        """
        try:
            if selector:
                element = self.page.locator(selector)
                element.filter(has_text=text).wait_for(
                    timeout=timeout or self.default_timeout
                )
            else:
                self.page.get_by_text(text).wait_for(
                    timeout=timeout or self.default_timeout
                )
            return True
        except PlaywrightTimeoutError:
            logger.error(f"Text not visible: {text}")
            return False
