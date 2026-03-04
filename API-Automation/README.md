# Lead Generation API Automation Framework

A comprehensive Python-based API automation framework for testing Lead Generation APIs with CI/CD integration.

## 📋 Features

- ✅ **7 API Endpoints Covered**: Create, Read, Update, Delete, List, Status, Bulk Import
- ✅ **Robust HTTP Client**: Auto-retry, authentication, logging
- ✅ **Data Validation**: Pydantic models for request/response
- ✅ **Custom Assertions**: Built-in API testing assertions
- ✅ **Rich Reporting**: HTML, Allure, and Coverage reports
- ✅ **CI/CD Ready**: Bitbucket Pipelines configuration
- ✅ **Parallel Execution**: Support for pytest-xdist
- ✅ **Security Testing**: XSS, SQL injection test cases
- ✅ **Performance Testing**: Response time validation

## 🏗️ Project Structure

```
API-Automation/
├── config/
│   ├── settings.py              # Configuration management
│   └── environments.yaml        # Environment configs
├── src/
│   ├── api_clients/
│   │   ├── base_client.py       # Base API client
│   │   └── lead_client.py       # Lead API client (7 endpoints)
│   ├── models/
│   │   └── lead_models.py       # Pydantic data models
│   └── utils/
│       ├── http_client.py       # HTTP client with retry
│       ├── logger.py            # Logging utility
│       └── assertions.py        # Custom assertions
├── tests/
│   ├── functional/              # Functional tests
│   │   ├── test_create_lead_api.py
│   │   ├── test_get_lead_api.py
│   │   ├── test_update_lead_api.py
│   │   ├── test_delete_lead_api.py
│   │   ├── test_list_leads_api.py
│   │   ├── test_lead_status_api.py
│   │   └── test_bulk_import_api.py
│   └── integration/             # Integration tests
├── ci-cd/
│   └── bitbucket-pipelines.yml  # CI/CD configuration
├── reports/                     # Test reports
├── logs/                        # Execution logs
├── conftest.py                  # Pytest fixtures
├── pytest.ini                  # Pytest configuration
├── run_tests.py                # Test runner script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-bitbucket-repo-url>
cd API-Automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configuration

Edit `.env` file with your API credentials:

```env
ENV=development
API_KEY=your_api_key
API_SECRET=your_api_secret
ACCESS_TOKEN=your_access_token
```

Update `config/environments.yaml` with your API endpoints:

```yaml
environments:
  development:
    base_url: "https://dev-api.yourcompany.com"
  staging:
    base_url: "https://staging-api.yourcompany.com"
  production:
    base_url: "https://api.yourcompany.com"
```

### 3. Run Tests

```bash
# Run all tests
python run_tests.py --all

# Run smoke tests only
python run_tests.py --smoke

# Run specific API tests
python run_tests.py --create    # Create Lead API
python run_tests.py --read      # Get Lead API
python run_tests.py --update    # Update Lead API
python run_tests.py --delete    # Delete Lead API
python run_tests.py --list      # List Leads API
python run_tests.py --status    # Lead Status API
python run_tests.py --bulk      # Bulk Import API

# Run with HTML report
python run_tests.py --all --html

# Run in parallel
python run_tests.py --all --parallel --workers 4

# Run on specific environment
python run_tests.py --smoke --env staging
```

## 📊 Test Coverage

| API Endpoint | Method | Test Cases |
|-------------|--------|------------|
| Create Lead | POST /api/v1/leads | TC-001 to TC-014 |
| Get Lead | GET /api/v1/leads/{id} | TC-015 to TC-021 |
| Update Lead | PUT /api/v1/leads/{id} | TC-022 to TC-027 |
| Delete Lead | DELETE /api/v1/leads/{id} | TC-028 to TC-032 |
| List Leads | GET /api/v1/leads | TC-033 to TC-043 |
| Lead Status | GET /api/v1/leads/{id}/status | TC-044 to TC-047 |
| Bulk Import | POST /api/v1/leads/bulk-import | TC-048 to TC-055 |

## 🔧 CI/CD Integration

### Bitbucket Pipelines

The framework includes a complete Bitbucket Pipelines configuration:

- **Pull Requests**: Lint check + Smoke tests
- **Main Branch**: Full regression tests
- **Manual Triggers**: Custom test runs
- **Release Tags**: Pre-release validation

### Pipeline Triggers

```bash
# Automatically runs on PR
# Automatically runs on merge to main

# Manual triggers in Bitbucket UI:
- smoke-tests
- full-regression
- production-smoke
```

## 📝 Adding New Test Cases

```python
# tests/functional/test_create_lead_api.py

import pytest
from src.models.lead_models import CreateLeadRequest

@pytest.mark.create
@pytest.mark.positive
class TestCreateLeadAPI:
    
    def test_create_lead_with_valid_data(self, api_client, sample_lead_data):
        """Your test case description"""
        response = api_client.create_lead(sample_lead_data)
        
        assert response.id is not None
        assert response.email == sample_lead_data.email
```

## 🐛 Debugging

```bash
# Run with verbose output
python run_tests.py --all --verbose

# Run single test
pytest tests/functional/test_create_lead_api.py::TestCreateLeadAPI::test_create_lead_with_valid_data -v

# Run with debugging
python run_tests.py --all --stop  # Stop on first failure

# Check logs
tail -f logs/api_automation_$(date +%Y-%m-%d).log
```

## 📈 Reports

### HTML Report
```bash
python run_tests.py --all --html
# Open: reports/report_YYYYMMDD_HHMMSS.html
```

### Allure Report
```bash
python run_tests.py --all --allure
allure serve reports/allure-results
```

### Coverage Report
```bash
python run_tests.py --all --coverage
# Open: reports/coverage/index.html
```

## 🔐 Security

- API credentials stored in environment variables
- Sensitive data masked in logs
- XSS and SQL injection test cases included
- Token refresh handling for authentication

## 📚 Documentation

- [Pytest Documentation](https://docs.pytest.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Requests Documentation](https://requests.readthedocs.io/)
- [Bitbucket Pipelines](https://support.atlassian.com/bitbucket-cloud/docs/bitbucket-pipelines-configuration-reference/)

## 🤝 Contributing

1. Create a feature branch
2. Add/update tests
3. Run linting: `black src tests && flake8 src tests`
4. Submit pull request

## 📄 License

Private - Internal use only
