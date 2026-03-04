# Allure E2E Flow Integration Guide

## ✅ Issue Fixed!
The `auto_run_full_flow.py` script now supports Allure reporting! Two methods are available:

---

## Method 1: Run Script with Allure Flag (Direct Execution)

Run the standalone script with `--allure` flag:

```bash
cd "/Users/rahulhajari/Learn AI/Final_upload"
source venv/bin/activate

# Run with Allure reporting enabled
python auto_run_full_flow.py --allure

# With custom results directory
python auto_run_full_flow.py --allure --allure-dir reports/allure-results
```

This generates Allure result files directly without needing pytest.

---

## Method 2: Run as Pytest Test (Recommended)

A new pytest test file has been created for better Allure integration:

```bash
cd "/Users/rahulhajari/Learn AI/Final_upload"
source venv/bin/activate

# Run E2E test with Allure
pytest tests/functional/test_e2e_full_flow.py -v --alluredir=reports/allure-results

# Run with detailed steps
pytest tests/functional/test_e2e_full_flow.py::TestE2EFullFlow::test_e2e_full_flow -v --alluredir=reports/allure-results
```

---

## View Allure Report

After running either method:

```bash
# Serve report dynamically
allure serve reports/allure-results

# Or generate static HTML
allure generate reports/allure-results -o reports/allure-html --clean
```

---

## Comparison

| Feature | Method 1 (Script) | Method 2 (Pytest) |
|---------|-------------------|-------------------|
| User Input | ✅ Interactive | ❌ Auto-generated |
| Allure Steps | ✅ Basic | ✅ Detailed |
| Attachments | ✅ JSON data | ✅ Rich content |
| Markers | ❌ No | ✅ @allure annotations |
| CI/CD Ready | ⚠️ Partial | ✅ Full |

---

## Example: Combined Workflow

```bash
# 1. Run E2E via pytest for detailed Allure report
pytest tests/functional/test_e2e_full_flow.py -v --alluredir=reports/allure-results

# 2. Add environment info
cat > reports/allure-results/environment.properties << 'EOF'
Environment=UAT
Test.Type=E2E
Platform=macOS
EOF

# 3. Generate and view report
allure serve reports/allure-results
```

---

## Troubleshooting

### Issue: "Allure results not showing"
**Solution**: Use `allure serve` command, don't open HTML files directly.

### Issue: "Test not found"
**Solution**: Ensure you're in the project root directory.

### Issue: "Import errors"
**Solution**: Activate virtual environment: `source venv/bin/activate`

---

## Files Changed

1. **auto_run_full_flow.py** - Added `AllureHelper` class and `--allure` flag
2. **tests/functional/test_e2e_full_flow.py** - New pytest test with full Allure decorators
3. **ALLURE_E2E_GUIDE.md** - This guide
