# Upstox Generate OTP API - Test Results

## API Details

| Detail | Value |
|--------|-------|
| Base URL | `https://service-uat.upstox.com` |
| Endpoint | `/login/open/v8/auth/1fa/otp-step/generate` |
| Method | POST |
| Query Param | `requestId=qatest4567` |

## Response Validations

The code validates the following:

1. ✅ **Status Code == 200**
2. ✅ **success == true** (for successful requests)
3. ✅ **validateOTPToken is generated** (present and not empty)

## Test Execution Results

### Test 1: Basic API Call
```python
from src.api_clients.upstox_auth_client import UpstoxAuthClient

client = UpstoxAuthClient(request_id='qatest4567')
response = client.generate_otp('9870165199')

# Validations:
# ✓ Status code verified: 200
# ✓ Success flag verified: true
# ✓ validateOTPToken generated
# ✓ Token saved for next API call
```

**Result:** ✅ PASSED

### Test 2: Token Storage
- Token automatically saved after successful generation
- Can be retrieved using `client.get_stored_token()`
- Stored in singleton `TokenStore` for sharing between APIs

**Result:** ✅ PASSED

### Test 3: Error Handling
The API handles various error scenarios:

| Error Scenario | Error Code | Message |
|----------------|------------|---------|
| Rate Limit | 1017069 | "You have exceeded the maximum number of times you can generate an OTP. Kindly, try again after 10 mins." |
| Invalid Mobile | 1017016 | "You have entered a invalid mobile number please enter the correct mobile number" |

**Result:** ✅ Error handling works correctly

## Response Structure

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "message": "Enter the 6-digit OTP received on 98****5199",
    "validateOTPToken": "ll1FA-55129540374a438d72ac6917edbfa3c162f097fa1c5cb25c5a008b179ab040ad",
    "nextRequestInterval": 120
  }
}
```

### Error Response (200 with success=false)
```json
{
  "success": false,
  "requestId": "JLGN-60112795-93e2-4242-a52a-6d02937afbbb",
  "error": {
    "code": 1017069,
    "message": "You have exceeded the maximum number of times you can generate an OTP. Kindly, try again after 10 mins."
  }
}
```

## Token Usage in Next API

The `validateOTPToken` is used in the subsequent API call (OTP Validation):

```
POST /login/open/v8/auth/1fa/otp-step/validate?requestId=qatest4567&validateOTPToken={TOKEN}
```

## Files Created

| File | Purpose |
|------|---------|
| `src/models/upstox_models.py` | Data models for Upstox API |
| `src/api_clients/upstox_auth_client.py` | API client for authentication |
| `tests/functional/test_upstox_generate_otp.py` | Test cases |
| `examples/generate_otp_example.py` | Usage examples |
| `demo_upstox_otp.py` | Standalone demo script |

## How to Run

```bash
# Activate virtual environment
source venv/bin/activate

# Run the demo
python demo_upstox_otp.py

# Run tests
python -m pytest tests/functional/test_upstox_generate_otp.py -v

# Run example
python examples/generate_otp_example.py
```

## Summary

✅ **Code is working correctly!**
- API connection successful
- All validations implemented
- Token storage working
- Error handling in place
- Ready for CI/CD integration
