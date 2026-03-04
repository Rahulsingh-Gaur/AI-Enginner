# Quick Start Guide - Run the Code in 30 Seconds! 🚀

## ⚡ Fastest Way (Copy & Paste)

### Option 1: Using the Run Script (Recommended)

```bash
# Go to project directory
cd "/Users/rahulhajari/Learn AI/API-Automation"

# Run quick test (default)
./run.sh

# Or run full realistic test suite
./run.sh realistic

# Or interactive mode
./run.sh interactive
```

---

## 🎯 Different Ways to Run (Choose Your Style)

### 1️⃣ **QUICK TEST** (5 seconds)
```bash
cd "/Users/rahulhajari/Learn AI/API-Automation"
source venv/bin/activate
./run.sh quick
```
**What it does:** Single API call to test connectivity

---

### 2️⃣ **REALISTIC TEST SUITE** (30 seconds)
```bash
cd "/Users/rahulhajari/Learn AI/API-Automation"
source venv/bin/activate
./run.sh realistic
```
**What it does:** 
- Scenario 1: Quick one-liner
- Scenario 2: Step-by-step with validations
- Scenario 3: Error handling demo
- Scenario 4: Batch testing (3 users)

**Output:**
```
======================================================================
UPSTOX API AUTOMATION - REALISTIC TEST SUITE
======================================================================

######################################################################
# Running: Quick One-Liner
######################################################################
✅ SUCCESS!
   Token: ll1FA-xxx...
   Profile ID: 3820874

######################################################################
# Running: Step-by-Step
######################################################################
✅ COMPLETE FLOW SUCCESSFUL!
   Generated Token: ll1FA-xxx...
   Verified Profile ID: 3820874

...

======================================================================
FINAL SUMMARY
======================================================================
✅ PASS: Quick One-Liner
✅ PASS: Step-by-Step
✅ PASS: Error Handling
✅ PASS: Batch Testing

Total: 4/4 scenarios passed
```

---

### 3️⃣ **INTERACTIVE MODE** (User friendly)
```bash
cd "/Users/rahulhajari/Learn AI/API-Automation"
source venv/bin/activate
./run.sh interactive
```
**What it shows:**
```
======================================================================
🔥 REAL-TIME UPSTOX OTP TOKEN GENERATOR
======================================================================
⏰ Current Time: 2026-02-19 15:45:30
======================================================================

📋 MENU:
   1️⃣  Generate OTP Token (with your mobile number)
   2️⃣  Check stored token
   3️⃣  Clear stored token
   4️⃣  Test with random mobile (avoid rate limit)
   5️⃣  View last response details
   0️⃣  Exit
-----------------------------------------------------------------------

👉 Enter your choice (0-5):
```

**Press `1` then Enter your mobile number to see it working!**

---

### 4️⃣ **PYTHON ONE-LINER** (For developers)
```bash
cd "/Users/rahulhajari/Learn AI/API-Automation"
source venv/bin/activate
python3 -c "
from src.api_clients.upstox_auth_client import complete_login_flow
result = complete_login_flow('9870165199', '123789')
print(f'Token: {result[\"token\"][:50]}...')
print(f'Profile ID: {result[\"profile_id\"]}')
"
```

---

### 5️⃣ **PYTEST** (For QA/Testing)
```bash
cd "/Users/rahulhajari/Learn AI/API-Automation"
source venv/bin/activate
./run.sh tests
```
**What it does:** Runs all 15 test cases with detailed output

---

### 6️⃣ **EXAMPLE SCRIPTS** (For learning)
```bash
cd "/Users/rahulhajari/Learn AI/API-Automation"
source venv/bin/activate
./run.sh example
```
**What it does:** Shows 5 different usage examples

---

## 📊 What Each Command Does

| Command | Time | Use Case | Output |
|---------|------|----------|--------|
| `./run.sh quick` | 5 sec | Quick check | Token + Profile ID |
| `./run.sh realistic` | 30 sec | Full testing | 4 scenario results |
| `./run.sh interactive` | Varies | Manual testing | Interactive menu |
| `./run.sh tests` | 10 sec | Automated QA | Test report |
| `./run.sh example` | 15 sec | Learning | 5 examples |
| `./run.sh mock` | 3 sec | No API calls | Mock demonstration |

---

## 🎬 Live Demo

### Watch it work step-by-step:

```bash
# 1. Quick test
$ ./run.sh quick

[INFO] Activating virtual environment...
[SUCCESS] Virtual environment activated
[INFO] Running quick test...
Testing complete login flow...
2026-02-19 15:45:30 | INFO | Generating OTP for mobile: 9870165199
2026-02-19 15:45:30 | INFO | ✓ Status code verified: 200
2026-02-19 15:45:30 | INFO | ✓ Success flag verified: true
2026-02-19 15:45:30 | INFO | ✓ validateOTPToken generated: ll1FA-xxx...
2026-02-19 15:45:31 | INFO | Verifying OTP (v4 endpoint)...
2026-02-19 15:45:31 | INFO | ✓ Status code verified: 200
2026-02-19 15:45:31 | INFO | ✓ All validations passed
✅ Token: ll1FA-37fac3f0b19cec51fa0d699cb2c9967c86e342ffab17e03065e5c05961737b3d...
✅ Profile ID: 3820874
✅ Test passed!

[SUCCESS] Done!
```

---

## 🆘 Troubleshooting

### Issue: "Virtual environment not found"
**Solution:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Module not found"
**Solution:**
```bash
source venv/bin/activate
cd "/Users/rahulhajari/Learn AI/API-Automation"
```

### Issue: "Rate limited"
**Solution:** Wait 10 minutes or use different mobile number
```bash
# Use random mobile
./run.sh interactive
# Then select option 4
```

### Issue: Permission denied
**Solution:**
```bash
chmod +x run.sh
chmod +x run_realistic_test.py
```

---

## 📁 All Available Commands

```bash
./run.sh help
```

Output:
```
Usage: ./run.sh [command]

Commands:
  quick       - Run quick one-liner test (default)
  realistic   - Run realistic test suite (4 scenarios)
  interactive - Start interactive menu
  tests       - Run pytest test suite
  all-tests   - Run all tests with coverage
  demo        - Run demo script
  example     - Run complete flow example
  mock        - Run mock test (no API calls)
  clean       - Clean up log files and cache
  help        - Show this help message
```

---

## ✅ Verification Checklist

Before running, verify:

- [ ] You're in the correct directory
- [ ] Virtual environment is activated
- [ ] Dependencies are installed
- [ ] You have internet connection
- [ ] Upstox API is accessible

Run this to verify:
```bash
cd "/Users/rahulhajari/Learn AI/API-Automation"
source venv/bin/activate
python3 -c "from src.api_clients.upstox_auth_client import UpstoxAuthClient; print('✅ Setup OK')"
```

---

## 🎯 Next Steps

After running successfully:

1. **Read the logs:** `tail -f logs/api_automation_*.log`
2. **Check reports:** `open reports/*.html` (if generated)
3. **Customize:** Edit `run_realistic_test.py` with your test data
4. **Integrate:** Use functions in your own scripts

---

## 💡 Pro Tips

1. **For quick testing:** Use `./run.sh quick`
2. **For debugging:** Use `./run.sh interactive`
3. **For CI/CD:** Use `./run.sh tests`
4. **For learning:** Use `./run.sh example`
5. **For documentation:** Check `REALISTIC_USAGE_GUIDE.md`

---

**Ready? Run this now:** 👇

```bash
cd "/Users/rahulhajari/Learn AI/API-Automation" && source venv/bin/activate && ./run.sh realistic
```

**That's it! You're now running the API automation in a realistic way! 🚀**
