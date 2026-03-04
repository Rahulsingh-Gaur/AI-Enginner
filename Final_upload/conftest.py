"""
Pytest Configuration and Fixtures
"""
import pytest
import uuid
from datetime import datetime
from faker import Faker

from src.api_clients.lead_client import LeadAPIClient
from src.models.lead_models import CreateLeadRequest, LeadSource, LeadStatus
from config.settings import Settings

# Initialize Faker for generating test data
faker = Faker()


# ═══════════════════════════════════════════════════════════════════
# SESSION FIXTURES
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def api_client():
    """Session-scoped API client"""
    client = LeadAPIClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def base_url():
    """Get base URL from settings"""
    return Settings.get_base_url()


# ═══════════════════════════════════════════════════════════════════
# FUNCTION FIXTURES
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def unique_email():
    """Generate unique email for test isolation"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def sample_lead_data(unique_email):
    """Generate sample lead data"""
    return CreateLeadRequest(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=unique_email,
        phone=faker.phone_number(),
        company=faker.company(),
        job_title=faker.job(),
        source=LeadSource.WEBSITE,
        status=LeadStatus.NEW,
        notes=f"Test lead created at {datetime.now().isoformat()}"
    )


@pytest.fixture
def created_lead(api_client, sample_lead_data):
    """
    Create a lead and return it
    Lead will be cleaned up after test
    """
    lead = api_client.create_lead(sample_lead_data)
    yield lead
    
    # Cleanup: Try to delete the lead
    try:
        api_client.delete_lead(lead.id)
    except:
        pass  # Ignore cleanup errors


@pytest.fixture
def multiple_leads(api_client):
    """Create multiple leads for list testing"""
    leads = []
    created_ids = []
    
    for i in range(5):
        data = CreateLeadRequest(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            source=LeadSource.WEBSITE,
            status=LeadStatus.NEW
        )
        lead = api_client.create_lead(data)
        leads.append(lead)
        created_ids.append(lead.id)
    
    yield leads
    
    # Cleanup
    for lead_id in created_ids:
        try:
            api_client.delete_lead(lead_id)
        except:
            pass


# ═══════════════════════════════════════════════════════════════════
# HOOKS
# ═══════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "smoke: Smoke tests")
    config.addinivalue_line("markers", "regression: Regression tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Auto-add markers based on test name
    for item in items:
        if "test_create" in item.nodeid:
            item.add_marker(pytest.mark.create)
        elif "test_get" in item.nodeid:
            item.add_marker(pytest.mark.read)
        elif "test_update" in item.nodeid:
            item.add_marker(pytest.mark.update)
        elif "test_delete" in item.nodeid:
            item.add_marker(pytest.mark.delete)
        elif "test_list" in item.nodeid:
            item.add_marker(pytest.mark.list)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test results and attach to report"""
    outcome = yield
    report = outcome.get_result()
    
    # Import allure here to avoid issues if not installed
    try:
        import allure
        
        # Attach API request/response info on failure
        if report.when == "call":
            if report.failed:
                # Attach error details to Allure
                allure.attach(
                    f"Test: {item.name}\nError: {report.longreprtext}",
                    name="Test Failure Details",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # Always attach test parameters for better traceability
            if item.funcargs:
                params = {k: str(v) for k, v in item.funcargs.items() if not callable(v)}
                if params:
                    allure.attach(
                        str(params),
                        name="Test Parameters",
                        attachment_type=allure.attachment_type.JSON
                    )
    except ImportError:
        pass  # Allure not installed, skip


# ═══════════════════════════════════════════════════════════════════
# COMMAND LINE OPTIONS
# ═══════════════════════════════════════════════════════════════════

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--env",
        action="store",
        default="development",
        help="Environment to run tests against (development, staging, production)"
    )
    parser.addoption(
        "--skip-cleanup",
        action="store_true",
        default=False,
        help="Skip test data cleanup"
    )
    parser.addoption(
        "--record-mode",
        action="store",
        default="none",
        help="Record mode for VCR (none, once, new_episodes, all)"
    )


@pytest.fixture(scope="session")
def environment(request):
    """Get environment from command line"""
    return request.config.getoption("--env")
