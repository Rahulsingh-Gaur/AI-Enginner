#!/usr/bin/env python3
"""
Auto Run Full 5-Stage Flow - User Input for Mobile Number!
========================================================
This script allows user to choose mobile number input method:
- Enter mobile number manually
- Auto-generate mobile number
Then runs all 5 stages: Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
- Generates ALLURE report
- Saves execution log
- Pushes results to Allure Report (use --allure flag)

Usage:
    python auto_run_full_flow.py
    python auto_run_full_flow.py --delay 5    # Wait 5 seconds before starting
    python auto_run_full_flow.py --allure     # Push results to Allure

NOTE: This script now uses the modular src/auto_flow package.
The actual implementation has been refactored into:
    - src/auto_flow/runner.py      (AutoTestRunner class)
    - src/auto_flow/stages.py      (StageManager class)
    - src/auto_flow/allure_helper.py (AllureHelper class)
    - src/auto_flow/cli.py         (CLI and main entry)

This file is kept for backward compatibility.
"""
import sys

# Import and run the modular CLI
from src.auto_flow.cli import main

if __name__ == "__main__":
    sys.exit(main())
