"""
Login Page Object Model.
Contains all elements and actions for the login page.
"""
from typing import Optional
from playwright.sync_api import Page, Locator

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """
    Page Object for Login Page.
    Maps to test cases: TC_LOGIN_001 through TC_LOGIN_025
    """
    
    # ==================== SELECTORS ====================
    # These selectors should be updated based on actual application
    
    # Input Fields
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    
    # Buttons
    SIGN_IN_BUTTON = "#log-in"  # Applitools demo site specific
    
    # Checkboxes
    REMEMBER_ME_CHECKBOX = ".form-check-input"  # Applitools demo site specific
    
    # Toggles (Not available on Applitools demo)
    PASSWORD_VISIBILITY_TOGGLE = "#password-toggle-not-available"
    
    # Messages (Applitools demo doesn't show error messages)
    ERROR_MESSAGE = ".error-message-not-available"
    USERNAME_ERROR = "#username-error-not-available"
    PASSWORD_ERROR = "#password-error-not-available"
    
    # Dashboard (for verification after login)
    DASHBOARD_ELEMENT = "text=Financial Overview"  # Applitools demo dashboard
    LOGOUT_BUTTON = "#logout-btn"
    
    # ==================== URL ====================
    LOGIN_PATH = "/index.html"  # Applitools demo site
    
    def __init__(self, page: Page, base_url: str):
        """
        Initialize LoginPage.
        
        Args:
            page: Playwright page instance
            base_url: Application base URL
        """
        super().__init__(page)
        self.base_url = base_url
        self.logger = logger
    
    # ==================== NAVIGATION ====================
    
    def navigate_to_login(self) -> "LoginPage":
        """
        Navigate to login page.
        TC_LOGIN_001-025: Preconditions
        """
        self.logger.info(f"Navigating to login page: {self.base_url}{self.LOGIN_PATH}")
        self.navigate_to(f"{self.base_url}{self.LOGIN_PATH}")
        self.wait_for_page_load()
        return self
    
    # ==================== FIELD ACTIONS ====================
    
    def enter_username(self, username: str) -> "LoginPage":
        """
        Enter username in the username field.
        TC_LOGIN_001, TC_LOGIN_003-009, TC_LOGIN_011-022
        
        Args:
            username: Username to enter
        """
        self.logger.info(f"Entering username: {username}")
        self.fill(self.USERNAME_INPUT, username)
        return self
    
    def enter_password(self, password: str) -> "LoginPage":
        """
        Enter password in the password field.
        TC_LOGIN_002-009, TC_LOGIN_011-022
        
        Args:
            password: Password to enter
        """
        self.logger.info(f"Entering password: {'*' * len(password)}")
        self.fill(self.PASSWORD_INPUT, password)
        return self
    
    def clear_username(self) -> "LoginPage":
        """Clear username field."""
        self.page.locator(self.USERNAME_INPUT).clear()
        return self
    
    def clear_password(self) -> "LoginPage":
        """Clear password field."""
        self.page.locator(self.PASSWORD_INPUT).clear()
        return self
    
    def get_username_value(self) -> str:
        """
        Get the value of username field.
        TC_LOGIN_013-014: Verify Remember Me functionality
        """
        return self.get_attribute(self.USERNAME_INPUT, "value") or ""
    
    def get_password_value(self) -> str:
        """Get the value of password field."""
        return self.get_attribute(self.PASSWORD_INPUT, "value") or ""
    
    # ==================== BUTTON ACTIONS ====================
    
    def click_sign_in(self) -> "LoginPage":
        """
        Click the Sign in button.
        TC_LOGIN_003-012, TC_LOGIN_015-022
        """
        self.logger.info("Clicking Sign in button")
        self.click(self.SIGN_IN_BUTTON)
        return self
    
    def click_sign_in_with_enter_key(self) -> "LoginPage":
        """
        Submit login form using Enter key.
        TC_LOGIN_021: Verify Sign in button click with Enter key
        """
        self.logger.info("Submitting form with Enter key")
        self.page.locator(self.PASSWORD_INPUT).press("Enter")
        return self
    
    def is_sign_in_button_enabled(self) -> bool:
        """
        Check if Sign in button is enabled.
        TC_LOGIN_010: Verify Sign in button is disabled/enabled states
        """
        return self.is_element_enabled(self.SIGN_IN_BUTTON)
    
    def is_sign_in_button_visible(self) -> bool:
        """Check if Sign in button is visible."""
        return self.is_element_visible(self.SIGN_IN_BUTTON)
    
    # ==================== CHECKBOX ACTIONS ====================
    
    def check_remember_me(self) -> "LoginPage":
        """
        Check the Remember Me checkbox.
        TC_LOGIN_013: Verify Remember Me checkbox functionality - checked
        """
        self.logger.info("Checking Remember Me checkbox")
        if not self.is_remember_me_checked():
            self.click(self.REMEMBER_ME_CHECKBOX)
        return self
    
    def uncheck_remember_me(self) -> "LoginPage":
        """
        Uncheck the Remember Me checkbox.
        TC_LOGIN_014: Verify Remember Me checkbox functionality - unchecked
        """
        self.logger.info("Unchecking Remember Me checkbox")
        if self.is_remember_me_checked():
            self.click(self.REMEMBER_ME_CHECKBOX)
        return self
    
    def is_remember_me_checked(self) -> bool:
        """Check if Remember Me is checked."""
        return self.page.locator(self.REMEMBER_ME_CHECKBOX).is_checked()
    
    # ==================== PASSWORD VISIBILITY ====================
    
    def toggle_password_visibility(self) -> "LoginPage":
        """
        Toggle password visibility.
        TC_LOGIN_020: Verify password visibility toggle
        """
        self.logger.info("Toggling password visibility")
        self.click(self.PASSWORD_VISIBILITY_TOGGLE)
        return self
    
    def is_password_masked(self) -> bool:
        """
        Check if password field is masked (type='password').
        TC_LOGIN_002: Verify password field masking functionality
        """
        input_type = self.get_attribute(self.PASSWORD_INPUT, "type")
        return input_type == "password"
    
    def is_password_visible(self) -> bool:
        """
        Check if password field is visible (type='text').
        TC_LOGIN_020: Verify password visibility toggle
        """
        input_type = self.get_attribute(self.PASSWORD_INPUT, "type")
        return input_type == "text"
    
    # ==================== ERROR MESSAGES ====================
    
    def get_error_message(self) -> str:
        """
        Get the error message text.
        TC_LOGIN_004-009, TC_LOGIN_011, TC_LOGIN_015-019, TC_LOGIN_022
        """
        if self.is_element_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def is_error_message_visible(self) -> bool:
        """
        Check if error message is displayed.
        TC_LOGIN_004-009, TC_LOGIN_011, TC_LOGIN_015
        """
        return self.is_element_visible(self.ERROR_MESSAGE)
    
    def get_username_error(self) -> str:
        """Get username field specific error."""
        if self.is_element_visible(self.USERNAME_ERROR):
            return self.get_text(self.USERNAME_ERROR)
        return ""
    
    def get_password_error(self) -> str:
        """Get password field specific error."""
        if self.is_element_visible(self.PASSWORD_ERROR):
            return self.get_text(self.PASSWORD_ERROR)
        return ""
    
    # ==================== LOGIN ACTIONS ====================
    
    def login(self, username: str, password: str) -> "LoginPage":
        """
        Perform login with given credentials.
        TC_LOGIN_003-012, TC_LOGIN_021
        
        Args:
            username: Username
            password: Password
        """
        self.logger.info(f"Performing login with username: {username}")
        self.enter_username(username)
        self.enter_password(password)
        self.click_sign_in()
        return self
    
    def login_with_remember_me(self, username: str, password: str) -> "LoginPage":
        """
        Perform login with Remember Me checked.
        TC_LOGIN_013: Verify Remember Me checkbox functionality - checked
        
        Args:
            username: Username
            password: Password
        """
        self.logger.info(f"Performing login with Remember Me for username: {username}")
        self.enter_username(username)
        self.enter_password(password)
        self.check_remember_me()
        self.click_sign_in()
        return self
    
    def logout(self) -> "LoginPage":
        """
        Perform logout.
        TC_LOGIN_013-014: Return to login page after logout
        """
        self.logger.info("Performing logout")
        if self.is_element_visible(self.LOGOUT_BUTTON):
            self.click(self.LOGOUT_BUTTON)
            self.wait_for_page_load()
        return self
    
    # ==================== VERIFICATION METHODS ====================
    
    def is_on_login_page(self) -> bool:
        """
        Check if current page is login page.
        TC_LOGIN_004-009, TC_LOGIN_011: User remains on login page
        """
        current_url = self.get_current_url()
        return self.LOGIN_PATH in current_url
    
    def is_on_dashboard(self) -> bool:
        """
        Check if user is on dashboard (successful login).
        TC_LOGIN_003, TC_LOGIN_012: User redirected to dashboard
        """
        return self.is_element_visible(self.DASHBOARD_ELEMENT)
    
    def is_username_field_visible(self) -> bool:
        """Check if username field is visible."""
        return self.is_element_visible(self.USERNAME_INPUT)
    
    def is_password_field_visible(self) -> bool:
        """Check if password field is visible."""
        return self.is_element_visible(self.PASSWORD_INPUT)
    
    def wait_for_error_message(self, timeout: Optional[int] = None) -> bool:
        """Wait for error message to appear."""
        return self.wait_for_selector(self.ERROR_MESSAGE, timeout)
    
    def wait_for_dashboard(self, timeout: Optional[int] = None) -> bool:
        """Wait for dashboard to load after successful login."""
        return self.wait_for_selector(self.DASHBOARD_ELEMENT, timeout)
    
    # ==================== FIELD VALIDATION ====================
    
    def get_username_max_length(self) -> int:
        """
        Get the maximum length attribute of username field.
        TC_LOGIN_017: Related to max length validation
        """
        max_length = self.get_attribute(self.USERNAME_INPUT, "maxlength")
        return int(max_length) if max_length else 0
    
    def get_password_max_length(self) -> int:
        """
        Get the maximum length attribute of password field.
        TC_LOGIN_017: Verify password field maximum length validation
        """
        max_length = self.get_attribute(self.PASSWORD_INPUT, "maxlength")
        return int(max_length) if max_length else 0
