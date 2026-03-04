#!/usr/bin/env python3
"""
Auto Run Full 5-Stage Flow - User Input for Mobile Number!
========================================================
This script allows user to choose mobile number input method:
- Enter mobile number manually
- Auto-generate mobile number
Then runs all 5 stages: Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
- Generates HTML + JSON reports
- Saves execution log

Usage:
    python auto_run_full_flow.py
    python auto_run_full_flow.py --delay 5    # Wait 5 seconds before starting
"""
import sys
import json
import logging
import argparse
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from src.api_clients.upstox_auth_client import UpstoxAuthClient
from src.models.upstox_models import token_store
from src.utils.mobile_generator import generate_unique_mobile
from src.utils.email_generator import generate_random_email


# Setup logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / f"auto_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AutoTestRunner:
    """Automatically runs all 5 stages with user input for mobile number"""
    
    def __init__(self):
        self.report_data = {
            "test_execution": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "timestamp": datetime.now().isoformat(),
                "environment": "UAT",
                "base_url": "https://service-uat.upstox.com"
            },
            "test_data": {},
            "api_results": [],
            "summary": {}
        }
        self.mobile_number = None
        self.email = None
        self.otp = "123789"
        self.client = None
    
    def get_mobile_number_from_user(self):
        """
        Ask user to choose mobile number input method:
        1. Enter mobile number manually
        2. Auto-generate mobile number
        """
        print("\n" + "=" * 70)
        print("📱 MOBILE NUMBER INPUT")
        print("=" * 70)
        print("\nChoose an option:")
        print("  1. Enter mobile number manually")
        print("  2. Auto-generate mobile number")
        print()
        
        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                # Manual input
                while True:
                    mobile = input("\nEnter 10-digit mobile number: ").strip()
                    
                    # Validate mobile number
                    if len(mobile) != 10:
                        print("❌ Error: Mobile number must be exactly 10 digits!")
                        continue
                    
                    if not mobile.isdigit():
                        print("❌ Error: Mobile number must contain only digits!")
                        continue
                    
                    if mobile[0] not in ['6', '7', '8', '9']:
                        print("❌ Error: Mobile number must start with 6, 7, 8, or 9!")
                        continue
                    
                    print(f"✅ Mobile number accepted: {mobile}")
                    return mobile
                    
            elif choice == "2":
                # Auto-generate
                mobile = generate_unique_mobile()
                print(f"\n✅ Auto-generated mobile number: {mobile}")
                return mobile
            
            else:
                print("❌ Invalid choice! Please enter 1 or 2.")
    
    def clear_and_setup(self):
        """Clear previous data and setup new test"""
        logger.info("=" * 70)
        logger.info("🚀 AUTO RUNNING COMPLETE 5-STAGE FLOW")
        logger.info("=" * 70)
        
        # Clear token store
        token_store.clear_all()
        logger.info("🗑️  Cleared previous session data")
        
        # Get mobile number from user
        self.mobile_number = self.get_mobile_number_from_user()
        
        # Generate email
        self.email = generate_random_email()
        
        self.report_data["test_data"] = {
            "mobile_number": self.mobile_number,
            "email": self.email,
            "otp_used": self.otp
        }
        
        logger.info(f"📱 Mobile Number: {self.mobile_number}")
        logger.info(f"📧 Auto-generated Email: {self.email}")
        logger.info(f"🔐 OTP: {self.otp}")
        logger.info("-" * 70)
        
    def stage1_generate_otp(self):
        """Stage 1: Generate OTP"""
        logger.info("\n📌 STAGE 1: Generate OTP")
        
        self.client = UpstoxAuthClient(request_id="qatest4567")
        response = self.client.generate_otp(self.mobile_number, save_token=True)
        
        success = response.success
        self.report_data["api_results"].append({
            "stage": 1,
            "api_name": "Generate OTP",
            "status": "PASS" if success else "FAIL",
            "status_code": 200,
            "message": response.message,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"   Status: {'✅ PASS' if success else '❌ FAIL'}")
        
        if not success:
            raise Exception("Stage 1 Failed: Generate OTP")
        
        return success
        
    def stage2_verify_otp(self):
        """Stage 2: Verify OTP"""
        logger.info("\n📌 STAGE 2: Verify OTP")
        
        response = self.client.verify_otp(
            otp=self.otp,
            mobile_number=self.mobile_number,
            save_profile_id=True
        )
        
        is_valid, error_msg = response.validate_success_response()
        
        self.report_data["api_results"].append({
            "stage": 2,
            "api_name": "Verify OTP",
            "status": "PASS" if is_valid else "FAIL",
            "status_code": 200,
            "message": response.message,
            "details": {
                "user_type": response.user_type,
                "profile_id": response.profile_id
            },
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Profile ID: {response.profile_id}")
        logger.info(f"   User Type: {response.user_type}")
        
        if not is_valid:
            raise Exception(f"Stage 2 Failed: {error_msg}")
        
        return is_valid
        
    def stage3_two_fa(self):
        """Stage 3: 2FA Authentication"""
        logger.info("\n📌 STAGE 3: 2FA Authentication")
        
        response = self.client.two_factor_auth(otp=self.otp)
        is_valid, error_msg = response.validate_success_response()
        
        self.report_data["api_results"].append({
            "stage": 3,
            "api_name": "2FA Authentication",
            "status": "PASS" if is_valid else "FAIL",
            "status_code": 200,
            "message": "2FA Successful",
            "details": {
                "redirect_uri": response.redirect_uri,
                "user_type": response.user_type,
                "customer_status": response.customer_status
            },
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Redirect URI: {response.redirect_uri}")
        logger.info(f"   Customer Status: {response.customer_status}")
        
        if not is_valid:
            raise Exception(f"Stage 3 Failed: {error_msg}")
        
        return is_valid
        
    def stage4_email_send_otp(self):
        """Stage 4: Email Send OTP"""
        logger.info("\n📌 STAGE 4: Email Send OTP")
        
        response = self.client.email_send_otp(email=self.email)
        is_valid, error_msg = response.validate_success_response()
        
        self.report_data["api_results"].append({
            "stage": 4,
            "api_name": "Email Send OTP",
            "status": "PASS" if is_valid else "FAIL",
            "status_code": 200,
            "message": response.message,
            "details": {
                "email_used": self.email
            },
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Email: {self.email}")
        logger.info(f"   Response: {response.message}")
        
        if not is_valid:
            raise Exception(f"Stage 4 Failed: {error_msg}")
        
        return is_valid
        
    def stage5_email_verify_otp(self):
        """Stage 5: Email Verify OTP"""
        logger.info("\n📌 STAGE 5: Email Verify OTP")
        
        response = self.client.email_verify_otp(email=self.email, otp=self.otp)
        is_valid, error_msg = response.validate_success_response()
        
        self.report_data["api_results"].append({
            "stage": 5,
            "api_name": "Email Verify OTP",
            "status": "PASS" if is_valid else "FAIL",
            "status_code": 200,
            "message": response.message,
            "details": {
                "email_verified": self.email
            },
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Email Verified: {self.email}")
        logger.info(f"   Response: {response.message}")
        
        if not is_valid:
            raise Exception(f"Stage 5 Failed: {error_msg}")
        
        return is_valid
        
    def run_all_stages(self):
        """Execute all 5 stages automatically"""
        try:
            # Setup
            self.clear_and_setup()
            
            # Stage 1
            self.stage1_generate_otp()
            
            # Stage 2
            self.stage2_verify_otp()
            
            # Stage 3
            self.stage3_two_fa()
            
            # Stage 4
            self.stage4_email_send_otp()
            
            # Stage 5
            self.stage5_email_verify_otp()
            
            # Collect final data
            all_data = self.client.get_all_stored_data()
            user_data = all_data.get('user_data', {})
            
            # Also check report_data for user_type from Stage 2 (fallback)
            user_type_from_report = None
            for result in self.report_data["api_results"]:
                if result.get("stage") == 2 and result.get("details"):
                    user_type_from_report = result["details"].get("user_type")
                    break
            
            self.report_data["summary"] = {
                "total_stages": 5,
                "passed": 5,
                "failed": 0,
                "success_rate": "100%",
                "overall_status": "PASS",
                "final_data": {
                    "mobile_number": self.mobile_number,
                    "email": self.email,
                    "profile_id": user_data.get("profile_id"),
                    "user_type": user_data.get("user_type") or user_type_from_report,
                    "customer_status": user_data.get("customer_status"),
                    "redirect_uri": user_data.get("redirect_uri"),
                    "email_send_status": user_data.get("email_response"),
                    "email_verify_status": user_data.get("email_verify_response")
                }
            }
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ ALL 5 STAGES COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"\n❌ TEST FAILED: {e}")
            self.report_data["summary"]["overall_status"] = "FAIL"
            self.report_data["summary"]["error"] = str(e)
            return False
            
        finally:
            if self.client:
                self.client.close()
                
    def generate_html_report(self, filename="reports/auto_test_report.html"):
        """Generate beautiful HTML report"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        summary = self.report_data["summary"]
        final_data = summary.get("final_data", {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upstox Auto Test Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .header h1 {{ color: #333; font-size: 2em; margin-bottom: 10px; }}
        .status-badge {{
            display: inline-block;
            padding: 10px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: bold;
            margin-top: 15px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .info-card {{
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .info-card h3 {{
            color: #667eea;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .info-card .value {{
            color: #333;
            font-size: 1.1em;
            font-weight: bold;
            word-break: break-all;
        }}
        .results-table {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .results-table h2 {{
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            font-size: 1.3em;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #555;
            border-bottom: 2px solid #e9ecef;
            font-size: 0.9em;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.95em;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-pass {{ background: #d4edda; color: #155724; }}
        .stage-badge {{
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        .footer {{
            text-align: center;
            color: white;
            opacity: 0.8;
            padding: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚀 Upstox Auto Test Report</h1>
            <p style="color: #666; margin-top: 10px;">
                Environment: <strong>UAT</strong> | 
                Date: <strong>{self.report_data['test_execution']['date']}</strong> | 
                Time: <strong>{self.report_data['test_execution']['time']}</strong>
            </p>
            <div class="status-badge">✅ ALL TESTS PASSED</div>
        </div>
        
        <!-- Key Information Grid -->
        <div class="info-grid">
            <div class="info-card">
                <h3>📱 Mobile Number</h3>
                <div class="value">{final_data.get('mobile_number', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>📧 Email Address</h3>
                <div class="value">{final_data.get('email', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>🆔 Profile ID</h3>
                <div class="value">{final_data.get('profile_id', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>👤 User Type</h3>
                <div class="value">{final_data.get('user_type', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>📊 Customer Status</h3>
                <div class="value">{final_data.get('customer_status', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>🔗 Redirect URI</h3>
                <div class="value" style="font-size: 0.9em;">{final_data.get('redirect_uri', 'N/A')}</div>
            </div>
        </div>
        
        <!-- Results Table -->
        <div class="results-table">
            <h2>📋 API Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Stage</th>
                        <th>API Name</th>
                        <th>Testing Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add rows for each API
        for result in self.report_data["api_results"]:
            html += f"""
                    <tr>
                        <td><span class="stage-badge">{result['stage']}</span></td>
                        <td><strong>{result['api_name']}</strong></td>
                        <td><span class="badge badge-pass">{result['status']}</span></td>
                    </tr>
"""
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Auto-Generated by Upstox API Automation Framework | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"📄 HTML Report saved: {filename}")
        return filename
        
    def generate_json_report(self, filename="reports/auto_test_report.json"):
        """Generate JSON report"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2)
        
        logger.info(f"📄 JSON Report saved: {filename}")
        return filename
        
    def print_final_summary(self):
        """Print final console summary"""
        summary = self.report_data["summary"]
        final_data = summary.get("final_data", {})
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST REPORT".center(80))
        print("=" * 80)
        
        print("\n🎯 TEST DATA:")
        print("-" * 80)
        print(f"  📱 Mobile Number:     {final_data.get('mobile_number', 'N/A')}")
        print(f"  📧 Email:             {final_data.get('email', 'N/A')}")
        print(f"  🆔 Profile ID:        {final_data.get('profile_id', 'N/A')}")
        print(f"  👤 User Type:         {final_data.get('user_type', 'N/A')}")
        print(f"  📊 Customer Status:   {final_data.get('customer_status', 'N/A')}")
        
        print(f"\n📋 API TEST RESULTS:")
        print("-" * 80)
        print(f"  {'Stage':<8} {'API Name':<25} {'Testing Status'}")
        print("-" * 80)
        
        for result in self.report_data["api_results"]:
            print(f"  {result['stage']:<8} {result['api_name']:<25} ✅ {result['status']}")
        
        print("-" * 80)
        print(f"\n📈 SUMMARY:")
        print(f"  Total Stages:  {summary.get('total_stages', 0)}")
        print(f"  Passed:        ✅ {summary.get('passed', 0)}")
        print(f"  Failed:        ❌ {summary.get('failed', 0)}")
        print(f"  Success Rate:  {summary.get('success_rate', '0%')}")
        print(f"\n  Overall Status: ✅ ALL TESTS PASSED")
        
        print("\n" + "=" * 80)
        print("🎉 EXECUTION COMPLETE!".center(80))
        print("=" * 80)


def main():
    """Main function with optional delay"""
    parser = argparse.ArgumentParser(description='Upstox API Auto Test Runner')
    parser.add_argument('--delay', type=int, default=0, help='Initial delay in seconds before starting')
    parser.add_argument('--skip-input', action='store_true', help='Skip mobile input and auto-generate')
    args = parser.parse_args()
    
    # Initial delay if specified (useful if server needs warmup)
    if args.delay > 0:
        print(f"\n⏳ Waiting {args.delay} seconds before starting...")
        time.sleep(args.delay)
    
    runner = AutoTestRunner()
    
    # Skip input if flag is set
    if args.skip_input:
        # Override the get_mobile_number_from_user method
        runner.get_mobile_number_from_user = lambda: generate_unique_mobile()
        print(f"\n✅ Auto-generating mobile number (skip-input flag set)")
    
    # Run all stages
    success = runner.run_all_stages()
    
    if success:
        # Generate reports
        runner.generate_html_report()
        runner.generate_json_report()
        
        # Print final summary
        runner.print_final_summary()
        
        print(f"\n📁 Reports saved in: reports/")
        print(f"📝 Log file: {log_file}")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
