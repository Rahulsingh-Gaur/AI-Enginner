#!/usr/bin/env python3
"""
Final Test Report Generator
============================
Generates beautiful HTML/Markdown test reports with all required fields.

Usage:
    python generate_test_report.py                    # Single test (with mobile input)
    python generate_test_report.py --bulk 10          # Bulk test (10 leads)
"""
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from src.api_clients.upstox_auth_client import UpstoxAuthClient
from src.models.upstox_models import token_store
from src.utils.mobile_generator import generate_unique_mobile
from src.utils.email_generator import generate_random_email


def get_mobile_number_from_user():
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


class TestReportGenerator:
    """Generates comprehensive test reports"""
    
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
        self.bulk_mode = False
        self.bulk_results = []
    
    def run_single_test(self, test_number=1):
        """Run single test and return results"""
        print(f"\n{'='*70}")
        if self.bulk_mode:
            print(f"🚀 Running Test #{test_number}...")
        else:
            print("🚀 Running Complete 5-Stage Test Suite...")
        print('='*70)
        
        client = UpstoxAuthClient(request_id="qatest4567")
        test_result = {
            "test_number": test_number,
            "timestamp": datetime.now().isoformat(),
            "status": "FAIL",
            "stages": []
        }
        
        try:
            # Get Test Data
            if self.bulk_mode:
                # Bulk mode: auto-generate mobile
                mobile = generate_unique_mobile()
            else:
                # Single test mode: ask user for mobile number
                mobile = get_mobile_number_from_user()
            
            email = generate_random_email()
            otp = "123789"
            
            test_result["mobile_number"] = mobile
            test_result["email"] = email
            test_result["otp_used"] = otp
            
            print(f"📱 Mobile: {mobile}")
            print(f"📧 Email: {email}")
            print("-" * 70)
            
            # Stage 1: Generate OTP
            stage1_response = client.generate_otp(mobile, save_token=True)
            stage1_pass = stage1_response.success
            test_result["stages"].append({
                "stage": 1,
                "api_name": "Generate OTP",
                "status": "PASS" if stage1_pass else "FAIL",
                "details": {"token_generated": bool(stage1_response.validate_otp_token)}
            })
            print(f"   Stage 1: {'✅ PASS' if stage1_pass else '❌ FAIL'}")
            
            if not stage1_pass:
                raise Exception("Stage 1 Failed")
            
            # Stage 2: Verify OTP
            stage2_response = client.verify_otp(otp=otp, mobile_number=mobile, save_profile_id=True)
            is_valid, _ = stage2_response.validate_success_response()
            test_result["stages"].append({
                "stage": 2,
                "api_name": "Verify OTP",
                "status": "PASS" if is_valid else "FAIL",
                "details": {
                    "user_type": stage2_response.user_type,
                    "profile_id": stage2_response.profile_id
                }
            })
            test_result["profile_id"] = stage2_response.profile_id
            test_result["user_type"] = stage2_response.user_type
            print(f"   Stage 2: {'✅ PASS' if is_valid else '❌ FAIL'} | Profile: {stage2_response.profile_id}")
            
            if not is_valid:
                raise Exception("Stage 2 Failed")
            
            # Stage 3: 2FA Authentication
            stage3_response = client.two_factor_auth(otp=otp)
            is_valid, _ = stage3_response.validate_success_response()
            test_result["stages"].append({
                "stage": 3,
                "api_name": "2FA Authentication",
                "status": "PASS" if is_valid else "FAIL",
                "details": {
                    "customer_status": stage3_response.customer_status
                }
            })
            test_result["customer_status"] = stage3_response.customer_status
            print(f"   Stage 3: {'✅ PASS' if is_valid else '❌ FAIL'} | Status: {stage3_response.customer_status}")
            
            if not is_valid:
                raise Exception("Stage 3 Failed")
            
            # Stage 4: Email Send OTP
            stage4_response = client.email_send_otp(email=email)
            is_valid, _ = stage4_response.validate_success_response()
            test_result["stages"].append({
                "stage": 4,
                "api_name": "Email Send OTP",
                "status": "PASS" if is_valid else "FAIL",
                "details": {"email_used": email}
            })
            print(f"   Stage 4: {'✅ PASS' if is_valid else '❌ FAIL'}")
            
            if not is_valid:
                raise Exception("Stage 4 Failed")
            
            # Stage 5: Email Verify OTP
            stage5_response = client.email_verify_otp(email=email, otp=otp)
            is_valid, _ = stage5_response.validate_success_response()
            test_result["stages"].append({
                "stage": 5,
                "api_name": "Email Verify OTP",
                "status": "PASS" if is_valid else "FAIL",
                "details": {"email_verified": email}
            })
            print(f"   Stage 5: {'✅ PASS' if is_valid else '❌ FAIL'}")
            
            if not is_valid:
                raise Exception("Stage 5 Failed")
            
            test_result["status"] = "PASS"
            test_result["overall"] = "✅ ALL PASS"
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            test_result["error"] = str(e)
            test_result["overall"] = "❌ FAILED"
        
        finally:
            client.close()
            token_store.clear_all()
        
        return test_result
    
    def run_bulk_tests(self, count=10):
        """Run multiple tests for bulk lead generation"""
        self.bulk_mode = True
        print(f"\n🚀 BULK TEST MODE: Running {count} tests...")
        print("=" * 70)
        
        for i in range(1, count + 1):
            result = self.run_single_test(test_number=i)
            self.bulk_results.append(result)
        
        # Calculate bulk summary
        passed = sum(1 for r in self.bulk_results if r["status"] == "PASS")
        failed = count - passed
        
        self.report_data["bulk_summary"] = {
            "total_tests": count,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/count)*100:.1f}%",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n{'='*70}")
        print("📊 BULK TEST SUMMARY")
        print('='*70)
        print(f"   Total Tests: {count}")
        print(f"   Passed: ✅ {passed}")
        print(f"   Failed: ❌ {failed}")
        print(f"   Success Rate: {(passed/count)*100:.1f}%")
        print('='*70)
    
    def generate_html_report(self, filename="reports/test_report.html"):
        """Generate beautiful HTML report"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        if self.bulk_mode:
            return self._generate_bulk_html_report(filename)
        else:
            return self._generate_single_html_report(filename)
    
    def _generate_single_html_report(self, filename):
        """Generate HTML report for single test"""
        result = self.bulk_results[0] if self.bulk_results else {}
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upstox API Test Report</title>
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
        }}
        .status-pass {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }}
        .status-fail {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); color: white; }}
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
        .badge-fail {{ background: #f8d7da; color: #721c24; }}
        .stage-badge {{
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        .details-cell {{
            font-size: 0.85em;
            color: #666;
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
            <h1>🚀 Upstox API Automation Test Report</h1>
            <p style="color: #666; margin-top: 10px;">
                Environment: <strong>{self.report_data['test_execution']['environment']}</strong> | 
                Date: <strong>{self.report_data['test_execution']['date']}</strong> | 
                Time: <strong>{self.report_data['test_execution']['time']}</strong>
            </p>
            <div class="status-badge {'status-pass' if result.get('status') == 'PASS' else 'status-fail'}">
                {result.get('overall', '❌ UNKNOWN')}
            </div>
        </div>
        
        <!-- Key Information Grid -->
        <div class="info-grid">
            <div class="info-card">
                <h3>📱 Mobile Number</h3>
                <div class="value">{result.get('mobile_number', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>📧 Email Address</h3>
                <div class="value">{result.get('email', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>🆔 Profile ID</h3>
                <div class="value">{result.get('profile_id', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>👤 User Type</h3>
                <div class="value">{result.get('user_type', 'N/A')}</div>
            </div>
            <div class="info-card">
                <h3>📊 Customer Status</h3>
                <div class="value">{result.get('customer_status', 'N/A')}</div>
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
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add rows for each stage
        for stage in result.get('stages', []):
            details = stage.get("details", {})
            # Remove token_length if present
            details.pop('token_length', None)
            details_str = "<br>".join([f"<strong>{k}:</strong> {v}" for k, v in details.items()])
            
            html += f"""
                    <tr>
                        <td><span class="stage-badge">{stage['stage']}</span></td>
                        <td><strong>{stage['api_name']}</strong></td>
                        <td><span class="badge {'badge-pass' if stage['status'] == 'PASS' else 'badge-fail'}">{stage['status']}</span></td>
                        <td class="details-cell">{details_str}</td>
                    </tr>
"""
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Upstox API Automation Framework | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n📄 HTML Report saved: {filename}")
        return filename
    
    def _generate_bulk_html_report(self, filename):
        """Generate HTML report for bulk tests"""
        summary = self.report_data.get("bulk_summary", {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upstox API Bulk Test Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .header h1 {{ color: #333; font-size: 2em; margin-bottom: 10px; }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            color: #667eea;
            font-size: 0.8em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .summary-card.pass {{ border-top: 4px solid #11998e; }}
        .summary-card.fail {{ border-top: 4px solid #eb3349; }}
        .leads-table {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .leads-table h2 {{
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
            font-size: 0.85em;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
        }}
        tr:hover {{ background: #f8f9fa; }}
        tr.pass {{ background: #f0fff4; }}
        tr.fail {{ background: #fff5f5; }}
        .badge {{
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75em;
            font-weight: bold;
        }}
        .badge-pass {{ background: #d4edda; color: #155724; }}
        .badge-fail {{ background: #f8d7da; color: #721c24; }}
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
            <h1>🚀 Upstox API Bulk Test Report</h1>
            <p style="color: #666; margin-top: 10px;">
                Bulk Lead Generation | {summary.get('total_tests', 0)} Leads | 
                Date: <strong>{self.report_data['test_execution']['date']}</strong>
            </p>
        </div>
        
        <!-- Summary Cards -->
        <div class="summary-cards">
            <div class="summary-card">
                <h3>Total Leads</h3>
                <div class="number">{summary.get('total_tests', 0)}</div>
            </div>
            <div class="summary-card pass">
                <h3>Passed</h3>
                <div class="number" style="color: #11998e;">{summary.get('passed', 0)}</div>
            </div>
            <div class="summary-card fail">
                <h3>Failed</h3>
                <div class="number" style="color: #eb3349;">{summary.get('failed', 0)}</div>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <div class="number">{summary.get('success_rate', '0%')}</div>
            </div>
        </div>
        
        <!-- Leads Table -->
        <div class="leads-table">
            <h2>📋 Generated Leads Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Mobile Number</th>
                        <th>Email</th>
                        <th>Profile ID</th>
                        <th>User Type</th>
                        <th>Customer Status</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add rows for each lead
        for result in self.bulk_results:
            row_class = "pass" if result.get('status') == 'PASS' else "fail"
            html += f"""
                    <tr class="{row_class}">
                        <td><strong>{result['test_number']}</strong></td>
                        <td>{result.get('mobile_number', 'N/A')}</td>
                        <td>{result.get('email', 'N/A')}</td>
                        <td>{result.get('profile_id', 'N/A')}</td>
                        <td>{result.get('user_type', 'N/A')}</td>
                        <td>{result.get('customer_status', 'N/A')}</td>
                        <td><span class="badge {'badge-pass' if result.get('status') == 'PASS' else 'badge-fail'}">{result.get('status', 'FAIL')}</span></td>
                    </tr>
"""
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Upstox API Automation Framework | Bulk Mode | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📄 Bulk HTML Report saved: {filename}")
        return filename
    
    def generate_json_report(self, filename="reports/test_report.json"):
        """Generate JSON report"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "test_execution": self.report_data['test_execution'],
            "results": self.bulk_results if self.bulk_mode else (self.bulk_results[0] if self.bulk_results else {})
        }
        
        if self.bulk_mode:
            data["bulk_summary"] = self.report_data.get("bulk_summary", {})
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"📄 JSON Report saved: {filename}")
        return filename
    
    def generate_csv_report(self, filename="reports/test_report.csv"):
        """Generate CSV report for bulk import"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Test #', 'Mobile Number', 'Email', 'Profile ID', 'User Type', 'Customer Status', 'Overall Status'])
            
            for result in self.bulk_results:
                writer.writerow([
                    result['test_number'],
                    result.get('mobile_number', ''),
                    result.get('email', ''),
                    result.get('profile_id', ''),
                    result.get('user_type', ''),
                    result.get('customer_status', ''),
                    result.get('status', 'FAIL')
                ])
        
        print(f"📄 CSV Report saved: {filename}")
        return filename
    
    def print_console_report(self):
        """Print console report"""
        print("\n" + "=" * 80)
        if self.bulk_mode:
            print("📊 BULK TEST REPORT".center(80))
        else:
            print("📊 TEST REPORT".center(80))
        print("=" * 80)
        
        if self.bulk_mode:
            summary = self.report_data.get("bulk_summary", {})
            print(f"\n📈 BULK SUMMARY:")
            print(f"   Total Tests: {summary.get('total_tests', 0)}")
            print(f"   Passed: ✅ {summary.get('passed', 0)}")
            print(f"   Failed: ❌ {summary.get('failed', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', '0%')}")
            
            print(f"\n📋 GENERATED LEADS:")
            print("-" * 80)
            print(f"   {'#':<4} {'Mobile':<12} {'Email':<25} {'Profile ID':<12} {'Status':<8}")
            print("-" * 80)
            for result in self.bulk_results:
                status_icon = "✅" if result.get('status') == 'PASS' else "❌"
                print(f"   {result['test_number']:<4} {result.get('mobile_number', 'N/A'):<12} {result.get('email', 'N/A'):<25} {str(result.get('profile_id', 'N/A')):<12} {status_icon} {result.get('status', 'FAIL')}")
        else:
            result = self.bulk_results[0] if self.bulk_results else {}
            print(f"\n🎯 TEST DATA:")
            print("-" * 80)
            print(f"  📱 Mobile Number:     {result.get('mobile_number', 'N/A')}")
            print(f"  📧 Email:             {result.get('email', 'N/A')}")
            print(f"  🆔 Profile ID:        {result.get('profile_id', 'N/A')}")
            print(f"  👤 User Type:         {result.get('user_type', 'N/A')}")
            print(f"  📊 Customer Status:   {result.get('customer_status', 'N/A')}")
            
            print(f"\n📋 API TEST RESULTS:")
            print("-" * 80)
            print(f"  {'Stage':<8} {'API Name':<20} {'Testing Status'}")
            print("-" * 80)
            for stage in result.get('stages', []):
                status_icon = "✅" if stage['status'] == "PASS" else "❌"
                print(f"  {stage['stage']:<8} {stage['api_name']:<20} {status_icon} {stage['status']}")
            
            print("-" * 80)
            print(f"\n📈 SUMMARY:")
            print(f"  Overall Status: {result.get('overall', '❌ UNKNOWN')}")
        
        print("\n" + "=" * 80)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Upstox API Test Report Generator')
    parser.add_argument('--bulk', type=int, metavar='N', help='Run N bulk tests')
    args = parser.parse_args()
    
    print("\n🚀 Upstox API Test Report Generator")
    print("=" * 70)
    
    generator = TestReportGenerator()
    
    if args.bulk:
        # Bulk mode
        generator.run_bulk_tests(count=args.bulk)
        generator.print_console_report()
        
        print("\n📄 Generating Reports...")
        print("-" * 70)
        generator.generate_html_report("reports/bulk_test_report.html")
        generator.generate_json_report("reports/bulk_test_report.json")
        generator.generate_csv_report("reports/bulk_test_report.csv")
        
        print(f"\n✅ Bulk reports generated!")
        print(f"   📄 HTML: reports/bulk_test_report.html")
        print(f"   📄 JSON: reports/bulk_test_report.json")
        print(f"   📄 CSV:  reports/bulk_test_report.csv")
    else:
        # Single test mode - store result in bulk_results for report generation
        result = generator.run_single_test()
        generator.bulk_results.append(result)  # Add to list for report generation
        generator.print_console_report()
        
        print("\n📄 Generating Reports...")
        print("-" * 70)
        generator.generate_html_report("reports/test_report.html")
        generator.generate_json_report("reports/test_report.json")
        
        print(f"\n✅ Reports generated!")
        print(f"   📄 HTML: reports/test_report.html")
        print(f"   📄 JSON: reports/test_report.json")


if __name__ == "__main__":
    main()
