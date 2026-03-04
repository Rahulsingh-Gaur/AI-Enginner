# API Automation Workflow - Visual Guide

## 🎯 Simple Analogy

Think of API Automation like **ordering food online**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ONLINE FOOD ORDERING                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  YOU (Customer)           APP (Client)           RESTAURANT (API)│
│      │                        │                       │         │
│      │ 1. Open app            │                       │         │
│      │───────────────────────>│                       │         │
│      │                        │                       │         │
│      │ 2. Enter details       │                       │         │
│      │───────────────────────>│                       │         │
│      │                        │                       │         │
│      │ 3. Place order         │                       │         │
│      │───────────────────────>│                       │         │
│      │                        │ 4. Send order         │         │
│      │                        │──────────────────────>│         │
│      │                        │                       │         │
│      │                        │ 5. Get confirmation   │         │
│      │                        │<──────────────────────│         │
│      │                        │                       │         │
│      │ 6. Show confirmation   │                       │         │
│      │<───────────────────────│                       │         │
│      │                        │                       │         │
└─────────────────────────────────────────────────────────────────┘
```

**In API Terms:**
- **YOU** = Test Script
- **APP** = API Client (our code)
- **RESTAURANT** = Upstox Server
- **ORDER** = API Request
- **CONFIRMATION** = API Response

---

## 🔄 Our Framework Workflow

### Step-by-Step Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                    UPSTOX OTP GENERATION FLOW                        │
└──────────────────────────────────────────────────────────────────────┘

STEP 1: TEST SCRIPT STARTS
═══════════════════════════════════════════════════════════════════════

  You run: python real_time_test.py
  │
  ▼
┌─────────────────┐
│  Test Script    │  "I want to generate OTP for mobile 9870165199"
└────────┬────────┘
         │
         ▼

STEP 2: CREATE API CLIENT
═══════════════════════════════════════════════════════════════════════

┌─────────────────┐     Creates     ┌──────────────────────────────┐
│  Test Script    │────────────────>│    UpstoxAuthClient          │
│                 │                 │    • Knows base URL          │
│                 │                 │    • Sets headers            │
│                 │                 │    • Validates responses     │
└─────────────────┘                 └──────────────┬───────────────┘
                                                   │
                                                   ▼
                                         ┌──────────────────┐
                                         │   HTTP Client    │
                                         │   (sends actual  │
                                         │    HTTP requests)│
                                         └──────────────────┘

STEP 3: PREPARE REQUEST
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────┐
│   UpstoxAuthClient      │
│                         │
│   Building Request:     │
│   ├─ URL: https://service-uat.upstox.com/login/open/v8/auth/1fa/otp-step/generate
│   ├─ Query: ?requestId=qatest4567
│   ├─ Method: POST
│   ├─ Headers:
│   │  ├─ X-Device-Details: platform=WEB|deviceId=...
│   │  └─ Content-Type: application/json
│   └─ Body:
│      └─ {"data": {"mobileNumber": "9870165199"}}
└───────────┬─────────────┘
            │
            ▼

STEP 4: SEND HTTP REQUEST
═══════════════════════════════════════════════════════════════════════

      Your Computer                                    Upstox Server
            │                                                  │
            │  POST /login/open/v8/auth/1fa/otp-step/generate  │
            │  ?requestId=qatest4567                           │
            │  ─────────────────────────────────────────────>  │
            │                                                  │
            │  Headers:                                        │
            │    X-Device-Details: platform=WEB|...            │
            │    Content-Type: application/json                │
            │                                                  │
            │  Body:                                           │
            │    {"data": {"mobileNumber": "9870165199"}}      │
            │                                                  │
            │                       (Server processes request) │
            │                                                  │
            │  HTTP/1.1 200 OK                                 │
            │  Content-Type: application/json                  │
            │  <─────────────────────────────────────────────  │
            │                                                  │
            │  Body:                                           │
            │  {                                               │
            │    "success": true,                              │
            │    "data": {                                     │
            │      "message": "Enter the 6-digit OTP...",      │
            │      "validateOTPToken": "ll1FA-xxx...",         │
            │      "nextRequestInterval": 120                 │
            │    }                                             │
            │  }                                               │
            │                                                  │

STEP 5: VALIDATE RESPONSE
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────┐
│   UpstoxAuthClient      │
│   receives response     │
│                         │
│   Validations:          │
│   ✓ Status code == 200  │
│   ✓ success == true     │
│   ✓ validateOTPToken    │
│     exists              │
└───────────┬─────────────┘
            │
            ▼

STEP 6: PARSE AND STORE
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────┐
│   GenerateOTPResponse   │  ← Pydantic Model validates structure
│   (Data Model)          │
│                         │
│   Extracted Data:       │
│   ├─ success: true      │
│   ├─ message: "Enter..."│
│   └─ validateOTPToken:  │
│      "ll1FA-xxx..."     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     TokenStore          │  ← Singleton (shared across code)
│                         │
│   Saves token:          │
│   Key: "validate_otp_token"
│   Value: "ll1FA-xxx..." │
└─────────────────────────┘

STEP 7: RETURN TO TEST
═══════════════════════════════════════════════════════════════════════

┌─────────────────┐     Returns     ┌──────────────────────────────┐
│  Test Script    │<────────────────│    UpstoxAuthClient          │
│                 │    response     │                              │
│  Can now use:   │                 └──────────────────────────────┘
│  response.      │
│  validate_otp_token
│                 │
│  Or retrieve:   │
│  token_store.   │
│  get_token()    │
└─────────────────┘

STEP 8: USE IN NEXT API
═══════════════════════════════════════════════════════════════════════

Next API Call (Validate OTP):

GET /login/open/v8/auth/1fa/otp-step/validate
?requestId=qatest4567
&validateOTPToken=ll1FA-xxx...    ← Token from Step 6!

```

---

## 🏗️ Framework Components Interaction

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FRAMEWORK ARCHITECTURE                        │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          TEST LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Test Case 1  │  │ Test Case 2  │  │ Test Case N  │              │
│  │ (Generate    │  │ (Validate    │  │ (Login)      │              │
│  │  OTP)        │  │  OTP)        │  │              │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                      │
└─────────┼──────────────────┼──────────────────┼──────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API CLIENT LAYER                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              UpstoxAuthClient                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │    │
│  │  │ generate_otp│  │validate_otp │  │   login     │         │    │
│  │  │    ()       │  │    ()       │  │    ()       │         │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │    │
│  │         │                │                │                │    │
│  │         └────────────────┴────────────────┘                │    │
│  │                          │                                 │    │
│  │         Uses ────────────┘                                 │    │
│  │                          │                                 │    │
│  │         ▼                                                  │    │
│  │  ┌─────────────────────────────────────────────────────┐   │    │
│  │  │              BaseAPIClient                          │   │    │
│  │  │  • Common authentication logic                      │   │    │
│  │  │  • Response handling                                │   │    │
│  │  └────────────────────────┬────────────────────────────┘   │    │
│  │                           │                                │    │
│  └───────────────────────────┼────────────────────────────────┘    │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        HTTP LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   HTTPClient                                │    │
│  │                                                             │    │
│  │  Features:                                                  │    │
│  │  • Retry on failure (3 attempts)                           │    │
│  │  • Timeout handling (30 seconds)                           │    │
│  │  • Logging (all requests/responses)                        │    │
│  │  • Session management (cookies, headers)                   │    │
│  │                                                             │    │
│  │  Methods:                                                   │    │
│  │  • get()  • post()  • put()  • delete()                    │    │
│  │                                                             │    │
│  └───────────────────────────┬─────────────────────────────────┘    │
│                              │                                       │
└──────────────────────────────┼───────────────────────┬───────────────┘
                               │                       │
                               ▼                       ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   requests      │    │   urllib3       │
                    │   library       │    │   (low-level)   │
                    └────────┬────────┘    └─────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    NETWORK LAYER                                     │
│                                                                      │
│  HTTPS Connection to: service-uat.upstox.com                        │
│  Port: 443                                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow in Code

### Simple Code Example

```python
# 1. IMPORT
from src.api_clients.upstox_auth_client import UpstoxAuthClient

# 2. CREATE CLIENT (Step 2 in diagram)
client = UpstoxAuthClient(request_id="qatest4567")

# 3. CALL API (Steps 3-5 in diagram)
response = client.generate_otp("9870165199")

# 4. USE RESPONSE (Step 7 in diagram)
print(response.validate_otp_token)  # "ll1FA-xxx..."
```

### What Happens Behind the Scenes

```
┌─────────────────────────────────────────────────────────────────────┐
│  CODE LINE              │  WHAT ACTUALLY HAPPENS                    │
├─────────────────────────────────────────────────────────────────────┤
│                         │                                           │
│  client =               │  • Create UpstoxAuthClient object         │
│  UpstoxAuthClient()     │  • Set base URL                           │
│                         │  • Setup default headers                  │
│                         │  • Create HTTP session                    │
│                         │                                           │
├─────────────────────────────────────────────────────────────────────┤
│                         │                                           │
│  response =             │  • Build URL with query params            │
│  client.                │  • Create JSON payload                    │
│  generate_otp()         │  • Call HTTP POST                         │
│                         │  • Wait for response                      │
│                         │  • Check status code == 200               │
│                         │  • Parse JSON                             │
│                         │  • Validate success == true               │
│                         │  • Extract validateOTPToken               │
│                         │  • Save token to TokenStore               │
│                         │  • Return response object                 │
│                         │                                           │
├─────────────────────────────────────────────────────────────────────┤
│                         │                                           │
│  response.              │  • Get value from parsed data             │
│  validate_otp_token     │  • Return token string                    │
│                         │                                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Visual: Original vs Framework Code

### Original Code (Basic)
```
┌────────────┐      ┌────────────┐      ┌────────────┐
│   Script   │─────>│  requests  │─────>│   Server   │
│   (your    │      │  (library) │      │  (Upstox)  │
│   code)    │<─────│            │<─────│            │
└────────────┘      └────────────┘      └────────────┘
      │
      │ Just prints
      ▼
   Console
```

### Framework Code (Advanced)
```
                    ┌────────────────────────────────────────────────┐
                    │              FRAMEWORK LAYERS                   │
                    └────────────────────────────────────────────────┘
                                     │
┌──────────┐    ┌───────────────┐    │    ┌───────────────┐    ┌──────────┐
│  Test    │───>│   API Client  │───>│───>│  HTTP Client  │───>│  Server  │
│  Script  │    │   (validate,  │    │    │   (retry,     │    │ (Upstox) │
│          │    │    parse)     │    │    │    log)       │    │          │
│          │<───│               │<───│<───│               │<───│          │
└──────────┘    └───────────────┘    │    └───────────────┘    └──────────┘
      │                   │          │
      │                   ▼          │
      │           ┌───────────────┐  │
      │           │  Data Models  │  │
      │           │ (validation)  │  │
      │           └───────────────┘  │
      │                   │          │
      │                   ▼          │
      │           ┌───────────────┐  │
      └──────────>│  Token Store  │  │
                  │   (memory)    │  │
                  └───────────────┘  │
                                     │
                              ┌──────┴──────┐
                              │   Logging   │
                              │   & Reports │
                              └─────────────┘
```

---

## 🔑 Key Takeaways

1. **Framework adds structure** to basic API calls
2. **Each layer has a job**: Test → Client → HTTP → Network
3. **Validation happens automatically** - no manual checking needed
4. **Token is saved automatically** - available for next API
5. **Errors are handled gracefully** - code doesn't crash
6. **Reusable components** - same code works for different APIs

---

## 📝 Quick Reference

| If you want to... | Use this file... | Call this... |
|-------------------|------------------|--------------|
| Generate OTP | `upstox_auth_client.py` | `client.generate_otp("9870165199")` |
| Get saved token | `upstox_models.py` | `token_store.get_token("validate_otp_token")` |
| Run tests | `test_upstox_generate_otp.py` | `pytest tests/functional/test_upstox_generate_otp.py` |
| Interactive test | `real_time_test.py` | `python real_time_test.py` |
| See logs | `logs/` folder | Open `api_automation_YYYY-MM-DD.log` |

---

**Document Version:** 1.0  
**Created:** 2026-02-19  
**For:** Beginners in API Automation
