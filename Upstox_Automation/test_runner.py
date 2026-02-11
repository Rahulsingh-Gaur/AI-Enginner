#!/usr/bin/env python3
"""
Test Runner - Main Orchestrator
Runs all test flows and generates combined reports
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_cases.test_login_flow import TestLoginFlow
from test_cases.test_email_flow import TestEmailFlow
from reports.report_generator import generate_report, print_console_report


class TestRunner:
    """Main test runner class"""
    
    def __init__(self, test_data_path: str = "config/test_data.json"):
        """
        Initialize test runner
        
        Args:
            test_data_path: Path to test data JSON file
        """
        self.test_data_path = test_data_path
        self.all_results = []
        self.test_flows = []
    
    def register_flow(self, flow_class, flow_name: str):
        """
        Register a test flow
        
        Args:
            flow_class: Test flow class (e.g., TestLoginFlow)
            flow_name: Name of the test flow
        """
        self.test_flows.append({"class": flow_class, "name": flow_name})
    
    def run_all_flows(self) -> list:
        """
        Run all registered test flows
        
        Returns:
            Combined list of all test results
        """
        print("\n" + "=" * 70)
        print("🚀 UPSTOX AUTOMATION - TEST EXECUTION STARTED")
        print("=" * 70)
        print(f"📁 Test Data: {self.test_data_path}")
        print(f"🔢 Total Flows: {len(self.test_flows)}")
        
        for flow in self.test_flows:
            try:
                # Initialize test flow
                flow_instance = flow["class"](self.test_data_path)
                
                # Run all tests in this flow
                flow_results = flow_instance.run_all()
                
                # Collect results
                self.all_results.extend(flow_results)
                
                # Print flow summary
                flow_instance.print_summary()
                
            except Exception as e:
                print(f"❌ Error running {flow['name']}: {e}")
        
        return self.all_results
    
    def run_specific_flow(self, flow_name: str) -> list:
        """
        Run a specific test flow by name
        
        Args:
            flow_name: Name of the flow to run
            
        Returns:
            List of test results
        """
        for flow in self.test_flows:
            if flow["name"].lower() == flow_name.lower():
                flow_instance = flow["class"](self.test_data_path)
                return flow_instance.run_all()
        
        print(f"⚠️ Flow '{flow_name}' not found")
        return []
    
    def generate_reports(self, output_format: str = "all", output_dir: str = "reports"):
        """
        Generate test reports
        
        Args:
            output_format: Report format (html, json, all)
            output_dir: Directory to save reports
        """
        print("\n" + "=" * 70)
        print("📊 GENERATING REPORTS")
        print("=" * 70)
        
        # Print console report
        print_console_report(self.all_results)
        
        # Generate file reports
        generated = generate_report(self.all_results, output_format, output_dir)
        
        print("\n✅ Reports generated successfully!")
        for format_type, path in generated.items():
            print(f"   📄 {format_type.upper()}: {path}")
        
        return generated
    
    def get_combined_summary(self) -> dict:
        """Get combined summary of all test results"""
        total = len(self.all_results)
        passed = sum(1 for r in self.all_results if r.get("status") == "PASS")
        failed = sum(1 for r in self.all_results if r.get("status") == "FAIL")
        skipped = sum(1 for r in self.all_results if r.get("status") == "SKIP")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": round((passed / total * 100), 2) if total > 0 else 0
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Upstox Automation Test Runner")
    parser.add_argument(
        "--flow", "-f",
        choices=["login", "email", "all"],
        default="all",
        help="Test flow to run (default: all)"
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
    parser.add_argument(
        "--data", "-d",
        default="config/test_data.json",
        help="Path to test data JSON file"
    )
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = TestRunner(args.data)
    
    # Register test flows
    runner.register_flow(TestLoginFlow, "Login Flow")
    runner.register_flow(TestEmailFlow, "Email Flow")
    
    # Run tests
    if args.flow == "all":
        runner.run_all_flows()
    elif args.flow == "login":
        runner.run_specific_flow("Login Flow")
    elif args.flow == "email":
        runner.run_specific_flow("Email Flow")
    
    # Generate reports
    if args.report in ("html", "json", "all"):
        report_format = "all" if args.report == "all" else args.report
        runner.generate_reports(report_format, args.output)
    
    # Print final summary
    summary = runner.get_combined_summary()
    print("\n" + "=" * 70)
    print("🏁 FINAL SUMMARY")
    print("=" * 70)
    print(f"Total: {summary['total']} | ✅ Passed: {summary['passed']} | ❌ Failed: {summary['failed']} | 📈 Rate: {summary['pass_rate']}%")
    print("=" * 70)
    
    # Exit with appropriate code
    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
