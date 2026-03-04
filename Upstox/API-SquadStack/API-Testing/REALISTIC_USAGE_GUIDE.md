# Realistic Usage Guide - Upstox API Automation

## 🎯 Overview

This guide shows you how to run the API automation code in **real-world scenarios**:
- Single API calls
- Complete login flows
- Batch testing
- Scheduled automation
- CI/CD integration

---

## 📋 Prerequisites

Before running, ensure you have:

```bash
# 1. Navigate to project
cd "/Users/rahulhajari/Learn AI/API-Automation"

# 2. Activate virtual environment
source venv/bin/activate

# 3. Verify installation
python --version  # Should show Python 3.11+
pip list | grep -E "requests|pydantic|pytest"
```

---

## 🚀 Realistic Usage Scenarios

### Scenario 1: Quick Single Test (Developer/Debugging)

**Use case:** You're developing and want to quickly test if the API works

```bash
# Quick one-liner test
python3 -c "
from src.api_clients.upstox_auth_client import UpstoxAuthClient

client = UpstoxAuthClient()
response = client.generate_otp('9870165199')
print(f'Token: {response.validate_otp_token[:30] if response.validate_otp_token else \"None\"}...')
client.close()
"
```

**When to use:**
- Quick debugging
- Checking if API is up
- Verifying your changes

---

### Scenario 2: Complete Login Flow (End-to-End Testing)

**Use case:** Test the complete user journey

```python
# realistic_test_complete_flow.py
from src.api_clients.upstox_auth_client import complete_login_flow
import sys

def test_complete_flow():
    """Realistic end-to-end test"""
    print("="*70)
    print("REALISTIC TEST: Complete Login Flow")
    print("="*70)
    
    # Test data
    mobile_number = "9870165199"
    otp = "123789"
    
    try:
        print(f"\n📱 Mobile: {mobile_number}")
        print(f"🔐 OTP: {otp}")
        print("\n🚀 Starting flow...\n")
        
        # Execute complete flow
        result = complete_login_flow(mobile_number, otp)
        
        # Validate results
        assert result['token'] is not None, "Token should not be None"
        assert result['profile_id'] is not None, "Profile ID should not be None"
        assert isinstance(result['profile_id'], int), "Profile ID should be numeric"
        
        print("\n" + "="*70)
        print("✅ TEST PASSED")
        print("="*70)
        print(f"Token: {result['token'][:50]}...")
        print(f"Profile ID: {result['profile_id']}")
        print("="*70)
        
        return True
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"Error: {e}")
        print("="*70)
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
```

**Run it:**
```bash
python3 realistic_test_complete_flow.py
```

---

### Scenario 3: Batch Testing Multiple Users

**Use case:** Test with multiple mobile numbers (data-driven testing)

```python
# realistic_batch_test.py
from src.api_clients.upstox_auth_client import UpstoxAuthClient
import random
import time

def batch_test():
    """Test multiple mobile numbers"""
    print("="*70)
    print("BATCH TEST: Multiple Mobile Numbers")
    print("="*70)
    
    # Generate test data
    test_numbers = [
        f"98701{random.randint(1000, 9999)}"
        for _ in range(5)
    ]
    
    results = []
    
    client = UpstoxAuthClient()
    
    for i, mobile in enumerate(test_numbers, 1):
        print(f"\n{'-'*70}")
        print(f"Test {i}/5: {mobile}")
        print('-'*70)
        
        try:
            # Generate OTP
            gen_response = client.generate_otp(mobile)
            
            if not gen_response.validate_otp_token:
                print(f"⚠️  Failed to generate OTP: {gen_response.message}")
                results.append({"mobile": mobile, "status": "FAILED", "reason": gen_response.message})
                continue
            
            print(f"✅ OTP Generated")
            
            # Verify OTP
            verify_response = client.verify_otp(
                otp="123789",
                mobile_number=mobile,
                auto_retry=True
            )
            
            if verify_response.success and verify_response.profile_id:
                print(f"✅ Verified | Profile ID: {verify_response.profile_id}")
                results.append({
                    "mobile": mobile, 
                    "status": "PASSED", 
                    "profile_id": verify_response.profile_id
                })
            else:
                print(f"❌ Verification failed: {verify_response.message}")
                results.append({
                    "mobile": mobile, 
                    "status": "FAILED", 
                    "reason": verify_response.message
                })
            
            # Wait between tests to avoid rate limits
            if i < len(test_numbers):
                print(f"⏳ Waiting 2 seconds before next test...")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"mobile": mobile, "status": "ERROR", "reason": str(e)})
    
    client.close()
    
    # Print summary
    print("\n" + "="*70)
    print("BATCH TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"Total: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Errors: {errors} ⚠️")
    
    print("\nDetailed Results:")
    for r in results:
        status_icon = "✅" if r['status'] == 'PASSED' else "❌" if r['status'] == 'FAILED' else "⚠️"
        print(f"  {status_icon} {r['mobile']}: {r['status']}")
        if 'profile_id' in r:
            print(f"      Profile ID: {r['profile_id']}")
        if 'reason' in r:
            print(f"      Reason: {r['reason']}")
    
    print("="*70)

if __name__ == "__main__":
    batch_test()
```

**Run it:**
```bash
python3 realistic_batch_test.py
```

---

### Scenario 4: Scheduled Automation (Cron Job)

**Use case:** Run tests automatically every day

```python
# realistic_scheduled_test.py
from src.api_clients.upstox_auth_client import complete_login_flow
from datetime import datetime
import json
import os

def scheduled_health_check():
    """Health check that runs on schedule"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[{timestamp}] Starting health check...")
    
    try:
        # Run complete flow
        result = complete_login_flow("9870165199", "123789")
        
        # Prepare result
        health_status = {
            "timestamp": timestamp,
            "status": "HEALTHY",
            "token_generated": True,
            "otp_verified": True,
            "profile_id": result['profile_id']
        }
        
        print(f"[{timestamp}] ✅ Health check PASSED")
        
    except Exception as e:
        health_status = {
            "timestamp": timestamp,
            "status": "UNHEALTHY",
            "error": str(e)
        }
        print(f"[{timestamp}] ❌ Health check FAILED: {e}")
    
    # Save to log file
    log_file = "logs/health_check.jsonl"
    os.makedirs("logs", exist_ok=True)
    
    with open(log_file, "a") as f:
        f.write(json.dumps(health_status) + "\n")
    
    print(f"[{timestamp}] Log saved to {log_file}")
    
    return health_status['status'] == 'HEALTHY'

if __name__ == "__main__":
    scheduled_health_check()
```

**Set up cron job (Linux/Mac):**
```bash
# Edit crontab
crontab -e

# Add line to run every hour
0 * * * * cd "/Users/rahulhajari/Learn AI/API-Automation" && source venv/bin/activate && python3 realistic_scheduled_test.py >> logs/cron.log 2>&1

# Or run every day at 9 AM
0 9 * * * cd "/Users/rahulhajari/Learn AI/API-Automation" && source venv/bin/activate && python3 realistic_scheduled_test.py >> logs/cron.log 2>&1
```

---

### Scenario 5: Interactive Menu (Manual Testing)

**Use case:** Interactive testing with user input

```bash
# Run the interactive menu we already created
python3 real_time_test.py
```

**Menu Options:**
```
📋 MENU:
   1️⃣  Generate OTP Token (with your mobile number)
   2️⃣  Check stored token
   3️⃣  Clear stored token
   4️⃣  Test with random mobile (avoid rate limit)
   5️⃣  View last response details
   0️⃣  Exit
```

---

### Scenario 6: pytest Suite (Professional Testing)

**Use case:** Run complete test suite with reports

```bash
# Run all tests with verbose output
pytest tests/functional/test_upstox_verify_otp.py -v

# Run all tests with HTML report
pytest tests/functional/ -v --html=reports/test_report.html

# Run specific test
pytest tests/functional/test_upstox_verify_otp.py::test_verify_otp_response_model -v

# Run with coverage report
pytest tests/functional/ --cov=src --cov-report=html

# Run in parallel (faster)
pytest tests/functional/ -n auto
```

---

### Scenario 7: Load Testing (Performance)

**Use case:** Test API performance under load

```python
# realistic_load_test.py
from src.api_clients.upstox_auth_client import UpstoxAuthClient
import time
import statistics

def load_test():
    """Performance testing"""
    print("="*70)
    print("LOAD TEST: API Performance")
    print("="*70)
    
    num_requests = 10
    response_times = []
    
    client = UpstoxAuthClient()
    
    print(f"\nMaking {num_requests} requests...\n")
    
    for i in range(num_requests):
        start = time.time()
        
        try:
            response = client.generate_otp_raw(f"98701{i:04d}")
            status = response.status_code
        except Exception as e:
            status = f"Error: {e}"
        
        elapsed = time.time() - start
        response_times.append(elapsed)
        
        print(f"Request {i+1}: {elapsed:.3f}s | Status: {status}")
    
    client.close()
    
    # Statistics
    print("\n" + "="*70)
    print("PERFORMANCE SUMMARY")
    print("="*70)
    print(f"Total Requests: {num_requests}")
    print(f"Average Response Time: {statistics.mean(response_times):.3f}s")
    print(f"Min Response Time: {min(response_times):.3f}s")
    print(f"Max Response Time: {max(response_times):.3f}s")
    print(f"Median Response Time: {statistics.median(response_times):.3f}s")
    print("="*70)

if __name__ == "__main__":
    load_test()
```

**Run it:**
```bash
python3 realistic_load_test.py
```

---

## 📊 Test Data Management

### Using Test Data Files

```python
# realistic_test_from_file.py
import json
from src.api_clients.upstox_auth_client import UpstoxAuthClient

def test_from_json_file():
    """Load test data from JSON file"""
    
    # Create test data file
    test_data = {
        "test_cases": [
            {"mobile": "9870165191", "otp": "123789", "expected": "success"},
            {"mobile": "9870165192", "otp": "123789", "expected": "success"},
            {"mobile": "9870165193", "otp": "000000", "expected": "failure"}
        ]
    }
    
    with open("test_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    # Load and test
    with open("test_data.json", "r") as f:
        data = json.load(f)
    
    client = UpstoxAuthClient()
    
    for tc in data["test_cases"]:
        print(f"\nTesting: {tc['mobile']}")
        
        # Generate
        gen_response = client.generate_otp(tc['mobile'])
        
        if gen_response.validate_otp_token:
            # Verify
            verify_response = client.verify_otp(tc['otp'], auto_retry=False)
            
            actual = "success" if verify_response.success else "failure"
            expected = tc['expected']
            
            status = "✅ PASS" if actual == expected else "❌ FAIL"
            print(f"  {status} | Expected: {expected}, Got: {actual}")
        else:
            print(f"  ⚠️  Could not generate OTP")
    
    client.close()

if __name__ == "__main__":
    test_from_json_file()
```

---

## 🔐 Environment-Based Configuration

### Using .env File for Different Environments

```bash
# Create .env file
cat > .env << 'EOF'
# Environment
ENV=development

# API Configuration
UPSTOX_BASE_URL=https://service-uat.upstox.com
DEFAULT_REQUEST_ID=qatest4567
DEFAULT_OTP=123789

# Test Data
TEST_MOBILE_NUMBER=9870165199

# Retry Configuration
AUTO_RETRY=true
MAX_RETRIES=1
EOF
```

```python
# realistic_env_config.py
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Use in code
from src.api_clients.upstox_auth_client import UpstoxAuthClient

client = UpstoxAuthClient(
    request_id=os.getenv("DEFAULT_REQUEST_ID", "qatest4567")
)

mobile = os.getenv("TEST_MOBILE_NUMBER", "9870165199")
otp = os.getenv("DEFAULT_OTP", "123789")
auto_retry = os.getenv("AUTO_RETRY", "true").lower() == "true"

result = complete_login_flow(mobile, otp)
```

---

## 📈 Monitoring & Alerting

### With Slack Notifications

```python
# realistic_with_alerts.py
from src.api_clients.upstox_auth_client import complete_login_flow
import requests
import os

def test_with_slack_alert():
    """Send Slack notification on failure"""
    
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    try:
        result = complete_login_flow("9870165199", "123789")
        print("✅ Test passed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
        # Send Slack alert
        if webhook_url:
            message = {
                "text": f"🚨 Upstox API Test Failed!\nError: {e}"
            }
            requests.post(webhook_url, json=message)
            print("📨 Slack alert sent")

if __name__ == "__main__":
    test_with_slack_alert()
```

---

## 🎯 Best Practices Summary

### Do's ✅
- Use virtual environment
- Handle exceptions properly
- Add delays between batch requests
- Log all results
- Use configuration files
- Clean up resources (client.close())

### Don'ts ❌
- Hard-code sensitive data
- Run infinite loops without delays
- Ignore rate limits
- Skip error handling
- Forget to close connections

---

## 📞 Quick Command Reference

```bash
# Quick test
python3 -c "from src.api_clients.upstox_auth_client import complete_login_flow; print(complete_login_flow('9870165199', '123789'))"

# Run all tests
pytest tests/functional/ -v

# Interactive mode
python3 real_time_test.py

# With report
pytest tests/functional/ --html=report.html

# Check logs
tail -f logs/api_automation_$(date +%Y-%m-%d).log
```

---

**Choose the scenario that fits your needs!** 🚀
