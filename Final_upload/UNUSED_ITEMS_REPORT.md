# Unused Files & Code Analysis Report

## 🔴 HIGH PRIORITY - UNUSED FILES (Safe to Delete)

### 1. Test Files (Not Executed in Current Flow)
Since we only use `auto_run_full_flow.py` with `--allure` flag, these pytest test files are **NOT used**:

| File | Size | Status |
|------|------|--------|
| `tests/functional/test_e2e_full_flow.py` | 9.5 KB | ❌ NOT USED |
| `tests/functional/test_bulk_import_api.py` | 4.8 KB | ❌ NOT USED |
| `tests/functional/test_create_lead_api.py` | 7.3 KB | ❌ NOT USED |
| `tests/functional/test_get_lead_api.py` | 2.7 KB | ❌ NOT USED |
| `tests/functional/test_lead_status_api.py` | 1.8 KB | ❌ NOT USED |
| `tests/functional/test_list_leads_api.py` | 3.4 KB | ❌ NOT USED |
| `tests/functional/test_update_lead_api.py` | 3.3 KB | ❌ NOT USED |
| `tests/functional/test_upstox_generate_otp.py` | 8.5 KB | ❌ NOT USED |
| `tests/functional/test_upstox_verify_otp.py` | 14.5 KB | ❌ NOT USED |
| `tests/integration/__init__.py` | 0 B | ❌ NOT USED |

**Total Waste: ~56 KB + maintenance overhead**

---

### 2. Source Modules (Not Imported)

| File | Purpose | Status |
|------|---------|--------|
| `src/api_clients/lead_client.py` | Lead API Client | ❌ NOT USED (Only upstox_auth_client used) |
| `src/api_clients/base_client.py` | Base API Client | ⚠️ Indirectly used (parent class) |
| `src/models/lead_models.py` | Lead Data Models | ❌ NOT USED (Only upstox_models used) |
| `src/utils/assertions.py` | Assertion Helpers | ❌ NOT USED |
| `src/utils/http_client.py` | HTTP Client | ⚠️ Indirectly used via base_client |
| `config/settings.py` | Config Management | ❌ NOT USED |
| `config/environments.yaml` | Environment Config | ❌ NOT USED |

---

### 3. Standalone/Helper Files

| File | Purpose | Status |
|------|---------|--------|
| `generate_test_report.py` | Legacy report generator | ❌ NOT USED (Allure used instead) |
| `serve_report.py` | HTTP server for reports | ⚠️ Optional (only for local viewing) |
| `conftest.py` | Pytest fixtures | ❌ NOT USED (pytest not executed) |

---

## 🟡 MEDIUM PRIORITY - UNUSED CODE WITHIN FILES

### 4. Unused Functions in `upstox_auth_client.py`

```python
# These functions are defined but never called:
- generate_otp_token()      # Lines 865-885
- verify_otp_token()        # Lines 888-925
- complete_login_flow()     # Lines 928-1020
```

**Note:** Keep for future use or potential API calls.

---

### 5. Unused Methods in `UpstoxAuthClient` Class

```python
# Check if these are used:
- validate_otp()            # May not be used
- login()                   # May not be used
- Some email methods        # Check usage
```

---

### 6. Unused Imports

```python
# In auto_run_full_flow.py:
import json                    # ✅ Used
import logging                 # ✅ Used
import argparse                # ✅ Used
import time                    # ✅ Used
import uuid                    # ✅ Used
import os                      # ✅ Used
from pathlib import Path       # ✅ Used

# Unused in current flow but kept for potential use
```

---

## 🟢 LOW PRIORITY - UNUSED DOCUMENTATION

### 7. Documentation Files (Optional Cleanup)

| File | Purpose | Recommendation |
|------|---------|----------------|
| `**Role Accepted! 🛡️**.md` | Unknown | ❌ Delete (special chars in name) |
| `ALLURE_E2E_GUIDE.md` | Allure guide | ⚠️ Keep (useful) |
| `API 6 Step 6b.md` | API docs | ⚠️ Keep or Archive |
| `E2E_SETUP_SUMMARY.md` | Setup guide | ⚠️ Keep (useful) |
| `JENKINS_SETUP.md` | Jenkins guide | ✅ Keep (essential) |
| `Logic.md` | Logic documentation | ⚠️ Review content |
| `README.md` | Main readme | ✅ Keep (essential) |
| `WORKFLOW.md` | Workflow docs | ⚠️ Review content |

---

## 📊 CLEANUP RECOMMENDATIONS

### Immediate Cleanup (Safe to Delete)

```bash
# Remove unused test files
rm tests/functional/test_*.py
rm tests/integration/__init__.py

# Remove legacy report generator
rm generate_test_report.py

# Remove config (if not using different environments)
rm config/settings.py
rm config/environments.yaml
```

### Optional Cleanup

```bash
# Remove unused src modules (if confirmed not needed)
rm src/api_clients/lead_client.py
rm src/models/lead_models.py
rm src/utils/assertions.py
rm conftest.py
```

---

## 💾 DISK SPACE SAVED

| Category | Estimated Savings |
|----------|-------------------|
| Test Files | ~60 KB |
| Unused Src | ~30 KB |
| Documentation | ~20 KB |
| **Total** | **~110 KB** |

---

## ⚠️ IMPORTANT NOTES

1. **DO NOT DELETE** these essential files:
   - `auto_run_full_flow.py` (Main E2E script)
   - `src/api_clients/upstox_auth_client.py` (Core API client)
   - `src/models/upstox_models.py` (Data models)
   - `src/utils/mobile_generator.py` (Mobile gen)
   - `src/utils/email_generator.py` (Email gen)
   - `Jenkinsfile` (CI/CD config)
   - `requirements.txt` (Dependencies)

2. **Backup Before Deleting** - Use git to track deletions

3. **Test After Cleanup** - Run E2E flow to verify nothing broke

---

*Report generated: $(date)*
