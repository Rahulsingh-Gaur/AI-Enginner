# Test Execution Log

## Session Information

| Field | Value |
|-------|-------|
| **Test Name** | Happy Path Test |
| **Session ID** | 20260304_121408 |
| **Start Time** | 2026-03-04 12:14:08 |
| **End Time** | 2026-03-04 12:14:55 |
| **Duration** | 46.87 seconds |

## Execution Steps

### Step 1: OUTPUT: Test Start

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:08.728871  

**Message:** Happy Path Test initialized  
**Data:**
```json
{
  "mobile": "9552931377",
  "headless": false,
  "mode": "GUI"
}
```

---

### Step 2: OUTPUT: Browser Init

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:11.492796  

**Message:** Chrome browser initialized  
**Data:**
```json
{
  "headless": false
}
```

---

### Step 3: OUTPUT: Navigation

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:11.847695  

**Message:** Navigated to https://upstox.com/  
**Data:**
```json
{
  "url": "https://upstox.com/"
}
```

---

### Step 4: OUTPUT: Sign In

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:14.902841  

**Message:** Sign In button clicked  
---

### Step 5: INPUT: Mobile Number

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:28.108620  

**Field:** `Mobile Number`  
**Value:** `9552931377`   

---

### Step 6: OUTPUT: Get OTP

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:28.651615  

**Message:** Get OTP button clicked  
---

### Step 1: Mobile Entry

**Status:** ✅ PASS  
**Time:** 2026-03-04T12:14:31.338593  

**Details:**
```json
{
  "mobile": "9552931377"
}
```

---

### Step 8: OUTPUT: OTP Screen

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:34.443149  

**Message:** OTP screen not found - may be email flow  
---

### Step 9: OUTPUT: Email Screen

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:52.157511  

**Message:** Email screen not present - skipped  
---

### Step 10: OUTPUT: Final URL

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:52.161073  

**Message:** Current URL: https://login.upstox.com/  
**Data:**
```json
{
  "url": "https://login.upstox.com/"
}
```

---

### Step 11: OUTPUT: Final Check

**Status:** ℹ️ INFO  
**Time:** 2026-03-04T12:14:55.596397  

**Message:** OTP input not found  
---

### Step 3: Final Verification

**Status:** ❌ FAIL  
**Time:** 2026-03-04T12:14:55.596406  

**Details:**
```json
{
  "otp_screen": false
}
```

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Steps** | 12 |
| **Passed** | 1 ✅ |
| **Failed** | 1 ❌ |
| **Manual Intervention** | 0 ⚠️ |
| **Duration** | 46.87 seconds |

## Notes

- **Input:** User input fields captured with actual values (masked for sensitive data)
- **Output:** System responses and page states
- **Manual:** Steps requiring human intervention (e.g., OTP entry)
- **Screenshots:** Visual captures of key steps (if enabled)

---
*Auto-generated on 2026-03-04 12:14:55*
