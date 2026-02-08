"""
Pytest configuration and fixtures for the automation framework.
Includes comprehensive reporting and bug tracking.
"""
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from pathlib import Path
import os
import logging
from datetime import datetime

from config.settings import settings
from utils.logger import get_logger
from utils.report_generator import report_generator, TestResult

# Initialize logger
logger = get_logger(__name__)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "login: mark test as login test")
    config.addinivalue_line("markers", "critical: mark test as critical priority")
    config.addinivalue_line("markers", "high: mark test as high priority")
    config.addinivalue_line("markers", "medium: mark test as medium priority")
    config.addinivalue_line("markers", "low: mark test as low priority")


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    logger.info("=" * 60)
    logger.info("TEST SESSION STARTING")
    logger.info("=" * 60)
    report_generator.start_execution()


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    logger.info("=" * 60)
    logger.info("TEST SESSION FINISHED")
    logger.info("=" * 60)
    report_generator.finish_execution()
    
    # Print report locations
    print("\n" + "=" * 60)
    print("📊 REPORTS GENERATED")
    print("=" * 60)
    print(f"Reports directory: {settings.REPORT_DIR}/")
    print(f"Screenshots directory: {settings.SCREENSHOT_DIR}/")
    print("=" * 60 + "\n")


# ==================== Fixtures ====================

@pytest.fixture(scope="session")
def browser(request):
    """
    Create a browser instance for the test session.
    Yields the browser instance and closes it after all tests.
    """
    # Get browser from command line or settings
    browser_name = request.config.getoption("--browser") or settings.BROWSER
    headless = request.config.getoption("--headed") is False or settings.HEADLESS
    
    logger.info(f"Launching {browser_name} browser (headless={headless})")
    
    with sync_playwright() as p:
        browser_type = getattr(p, browser_name)
        browser_instance = browser_type.launch(
            headless=headless,
            slow_mo=settings.SLOW_MO
        )
        yield browser_instance
        logger.info("Closing browser")
        browser_instance.close()


@pytest.fixture(scope="function")
def context(browser: Browser):
    """
    Create a new browser context for each test function.
    Provides isolated session for each test.
    """
    logger.info("Creating new browser context")
    
    # Create video directory if it doesn't exist
    video_dir = Path("videos")
    video_dir.mkdir(exist_ok=True)
    
    context_instance = browser.new_context(
        viewport={
            "width": settings.VIEWPORT_WIDTH,
            "height": settings.VIEWPORT_HEIGHT
        },
        record_video_dir=str(video_dir)
    )
    
    # Set default timeout
    context_instance.set_default_timeout(settings.DEFAULT_TIMEOUT)
    context_instance.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
    
    yield context_instance
    
    logger.info("Closing browser context")
    context_instance.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """
    Create a new page for each test function.
    Provides a fresh page for each test.
    """
    logger.info("Creating new page")
    page_instance = context.new_page()
    yield page_instance
    logger.info("Closing page")


@pytest.fixture(scope="session")
def app_base_url(request):
    """
    Provide the base URL from settings or command line.
    Note: Renamed to avoid conflict with pytest-base-url plugin.
    """
    return request.config.getoption("--base-url") or settings.BASE_URL


@pytest.fixture(scope="function")
def test_info():
    """
    Fixture to store test information like steps and description.
    """
    return {
        "description": "",
        "steps": [],
        "test_data": {}
    }


# ==================== Test Hooks for Reporting ====================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and generate reports.
    This is called after each test phase (setup, call, teardown).
    """
    outcome = yield
    report = outcome.get_result()
    
    # Only process the 'call' phase (actual test execution)
    if report.when != "call":
        return
    
    # Get test information
    test_name = item.nodeid
    test_file = item.fspath.basename
    duration = report.duration
    timestamp = datetime.now().isoformat()
    
    # Get markers
    markers = [marker.name for marker in item.iter_markers()]
    
    # Get test description from docstring
    description = item.function.__doc__ or ""
    description = description.strip() if description else ""
    
    # Determine status
    if report.passed:
        status = "PASSED"
    elif report.skipped:
        status = "SKIPPED"
    elif report.failed:
        status = "FAILED"
    else:
        status = "ERROR"
    
    # Get error details if failed
    error_message = None
    error_type = None
    traceback = None
    
    if report.failed and call.excinfo:
        error_type = call.excinfo.type.__name__ if call.excinfo.type else "Unknown"
        error_message = str(call.excinfo.value) if call.excinfo.value else "Unknown error"
        
        # Get full traceback
        if call.excinfo.traceback:
            traceback = "\n".join(
                [str(frame) for frame in call.excinfo.traceback]
            )
    
    # Capture screenshot on failure
    screenshot_path = None
    video_path = None
    
    if report.failed and settings.SCREENSHOT_ON_FAILURE:
        page_fixture = None
        context_fixture = None
        
        for fixture_name in item.fixturenames:
            if fixture_name == "page":
                page_fixture = item.funcargs.get("page")
            elif fixture_name == "context":
                context_fixture = item.funcargs.get("context")
        
        if page_fixture:
            try:
                # Create screenshot directory
                screenshot_dir = Path(settings.SCREENSHOT_DIR)
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate screenshot filename
                test_name_clean = item.nodeid.replace("::", "_").replace("/", "_")[:100]
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"FAILED_{test_name_clean}_{timestamp_str}.png"
                screenshot_path = str(screenshot_dir / filename)
                
                # Take screenshot
                page_fixture.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot captured: {screenshot_path}")
                
            except Exception as e:
                logger.error(f"Failed to capture screenshot: {e}")
        
        # Get video path
        if context_fixture and hasattr(context_fixture, 'video'):
            try:
                video = context_fixture.video
                if video:
                    video_path = video.path()
            except:
                pass
    
    # Create test result
    test_result = TestResult(
        test_name=test_name,
        test_file=test_file,
        status=status,
        duration=duration,
        timestamp=timestamp,
        error_message=error_message,
        error_type=error_type,
        screenshot_path=screenshot_path,
        video_path=video_path,
        traceback=traceback,
        browser=settings.BROWSER,
        url=settings.BASE_URL,
        markers=markers,
        description=description,
        steps=[]  # Can be populated using test_info fixture
    )
    
    # Add to report generator
    report_generator.add_result(test_result)
    
    # Log result
    status_emoji = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⚠️", "ERROR": "🚨"}
    logger.info(f"{status_emoji.get(status, '❓')} {test_name} - {status} ({duration:.3f}s)")


def pytest_runtest_setup(item):
    """Setup hook called before each test."""
    logger.info(f"Starting test: {item.nodeid}")


def pytest_runtest_teardown(item):
    """Teardown hook called after each test."""
    logger.info(f"Finished test: {item.nodeid}")


# ==================== CLI Options ====================

# Note: pytest-playwright provides --browser, --headed, --base-url options
# We use environment variables for additional configuration

@pytest.fixture(scope="session", autouse=True)
def configure_settings():
    """Ensure settings are loaded from environment."""
    # Settings are already loaded from .env via config/settings.py
    pass
