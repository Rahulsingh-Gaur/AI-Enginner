#!/usr/bin/env python3
"""
Test Runner - Main Entry Point
Routes to Happy Path or Regression testing based on mode

Usage:
    python3 test_runner_new.py --mode happy        # Happy Path only
    python3 test_runner_new.py --mode regression   # Full regression (all validations)
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.happy_path_test import run_happy_path_test
from tests.regression_test import run_regression_test
from reports.report_generator import generate_report, print_console_report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Upstox Automation Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Happy Path test (GUI mode with browser)
  python3 test_runner_new.py --mode happy
  
  # Run Regression test (GUI mode with browser)
  python3 test_runner_new.py --mode regression
  
  # Run with specific report format
  python3 test_runner_new.py --mode happy --report html
  python3 test_runner_new.py --mode regression --report json
  
Note: GUI mode is required for OTP entry. CLI mode disabled.
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["happy", "regression"],
        required=True,
        help="Test mode: 'happy' for single flow, 'regression' for full validation"
    )
    
    parser.add_argument(
        "--report", "-r",
        choices=["html", "json", "console", "all"],
        default="all",
        help="Report format (default: all)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="reports",
        help="Output directory for reports (default: reports)"
    )
    
    # NOTE: CLI/Headless mode disabled - OTP requires GUI interaction
    # parser.add_argument(
    #     "--headless", "-hl",
    #     action="store_true",
    #     help="Run in CLI/Headless mode (no browser window)"
    # )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🚀 UPSTOX AUTOMATION - TEST RUNNER")
    print("=" * 70)
    print(f"📋 Mode: {args.mode.upper()}")
    print(f"📄 Report: {args.report}")
    print(f"👤 Mode: GUI (Browser window will open)")
    print("=" * 70)
    
    # Run the appropriate test (GUI mode only - CLI disabled for OTP)
    if args.mode == "happy":
        print("\n🟢 Running HAPPY PATH TEST...")
        print("   - Single complete login flow")
        print("   - Mobile: 9552931377")
        print("   - Email: Rahul.hajari@rksv.in")
        print("   - Flow: Mobile → OTP → Email → Continue")
        print("   - Note: GUI mode required for OTP entry\n")
        
        result = run_happy_path_test(headless=False)
        
    elif args.mode == "regression":
        print("\n🔴 Running REGRESSION TEST...")
        print("   - All mobile number validations")
        print("   - 13 Invalid + 4 Valid = 17 Total Tests")
        print("   - Tests format, length, series validation")
        print("   - Note: GUI mode required\n")
        
        result = run_regression_test(headless=False)
    
    else:
        print(f"❌ Unknown mode: {args.mode}")
        return 1
    
    # Convert result to report format
    report_results = []
    if "results" in result and isinstance(result["results"], list):
        for i, r in enumerate(result["results"], 1):
            report_result = {
                "tc_id": f"STEP-{i:02d}",
                "description": r.get("step", r.get("description", f"Step {i}")),
                "status": r.get("status", "UNKNOWN"),
                "details": r
            }
            report_results.append(report_result)
    else:
        # Single result format
        report_results = [{
            "tc_id": "TEST-01",
            "description": result.get("test_type", "Test"),
            "status": result.get("status", "UNKNOWN"),
            "details": result
        }]
    
    # Generate reports
    print("\n" + "=" * 70)
    print("📊 GENERATING REPORTS")
    print("=" * 70)
    
    # Console report
    if args.report in ("console", "all"):
        print_console_report(report_results)
    
    # File reports
    if args.report in ("html", "json", "all"):
        report_format = "all" if args.report == "all" else args.report
        generated = generate_report(report_results, report_format, args.output)
        
        print("\n✅ Reports generated:")
        for fmt, path in generated.items():
            print(f"   {fmt.upper()}: {path}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("🏁 TEST EXECUTION COMPLETE")
    print("=" * 70)
    print(f"Mode: {args.mode.upper()}")
    print(f"Status: {result.get('status', 'UNKNOWN')}")
    
    if "total_tests" in result:
        print(f"Total Tests: {result['total_tests']}")
        print(f"Passed: {result.get('passed', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
    
    print("=" * 70)
    
    # Return exit code
    return 0 if result.get("status") in ("PASS", "COMPLETE") else 1


if __name__ == "__main__":
    sys.exit(main())
