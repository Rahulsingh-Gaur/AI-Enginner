#!/usr/bin/env python3
"""
Report Generator Module
Generates test execution reports in various formats (HTML, JSON, Console)
"""

import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path


def generate_json_report(results: List[Dict], output_path: str = "reports/test_report.json") -> str:
    """
    Generate JSON report
    
    Args:
        results: List of test result dictionaries
        output_path: Path to save the JSON report
        
    Returns:
        Path to generated report file
    """
    report = {
        "metadata": {
            "project": "Upstox Automation",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        },
        "summary": calculate_summary(results),
        "results": results
    }
    
    # Ensure directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return output_path


def generate_html_report(results: List[Dict], output_path: str = "reports/test_report.html") -> str:
    """
    Generate HTML report
    
    Args:
        results: List of test result dictionaries
        output_path: Path to save the HTML report
        
    Returns:
        Path to generated report file
    """
    summary = calculate_summary(results)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upstox Automation - Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .card.pass .value {{ color: #28a745; }}
        .card.fail .value {{ color: #dc3545; }}
        .card.skip .value {{ color: #ffc107; }}
        .card.total .value {{ color: #007bff; }}
        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            margin-top: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        .results-table {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .results-table h2 {{
            padding: 20px;
            border-bottom: 1px solid #eee;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status.pass {{
            background: #d4edda;
            color: #155724;
        }}
        .status.fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status.skip {{
            background: #fff3cd;
            color: #856404;
        }}
        .error-msg {{
            color: #dc3545;
            font-size: 12px;
            margin-top: 5px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Upstox Automation - Test Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary-cards">
            <div class="card total">
                <h3>Total Tests</h3>
                <div class="value">{summary['total']}</div>
            </div>
            <div class="card pass">
                <h3>Passed</h3>
                <div class="value">{summary['passed']}</div>
            </div>
            <div class="card fail">
                <h3>Failed</h3>
                <div class="value">{summary['failed']}</div>
            </div>
            <div class="card skip">
                <h3>Skipped</h3>
                <div class="value">{summary['skipped']}</div>
            </div>
        </div>
        
        <div class="card">
            <h3>Pass Rate</h3>
            <div class="value" style="color: {'#28a745' if summary['pass_rate'] >= 80 else '#ffc107' if summary['pass_rate'] >= 50 else '#dc3545'};">
                {summary['pass_rate']:.1f}%
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {summary['pass_rate']}%"></div>
            </div>
        </div>
        
        <div class="results-table" style="margin-top: 20px;">
            <h2>📋 Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Description</th>
                        <th>User Input</th>
                        <th>Status</th>
                        <th>Execution Time</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_table_rows(results)}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Upstox Automation Framework v1.0 | Report generated automatically</p>
        </div>
    </div>
</body>
</html>"""
    
    # Ensure directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    return output_path


def generate_table_rows(results: List[Dict]) -> str:
    """Generate HTML table rows from results"""
    rows = []
    for result in results:
        status_class = result.get("status", "SKIP").lower()
        details = result.get("details", {})
        exec_time = details.get("execution_time", "-")
        
        # Get user input - check multiple possible locations
        user_input = result.get('user_input') or details.get('mobile') or details.get('email') or details.get('input') or details.get('number') or '-'
        
        # Format user input for display
        if user_input and user_input != '-':
            user_input_display = f"<code style='background:#f4f4f4;padding:2px 6px;border-radius:4px;'>{user_input}</code>"
        else:
            user_input_display = '-'
        
        row = f"""
        <tr>
            <td><strong>{result.get('tc_id', 'N/A')}</strong></td>
            <td>{result.get('description', 'No description')}</td>
            <td>{user_input_display}</td>
            <td><span class="status {status_class}">{result.get('status', 'SKIP')}</span></td>
            <td>{exec_time}s</td>
            <td>
                {result.get('error', details.get('message', '-')) if result.get('error') else details.get('message', '-')}
            </td>
        </tr>
        """
        rows.append(row)
    
    return "".join(rows)


def calculate_summary(results: List[Dict]) -> Dict:
    """Calculate summary statistics from results"""
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    skipped = sum(1 for r in results if r.get("status") == "SKIP")
    
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": round((passed / total * 100), 2) if total > 0 else 0
    }


def generate_report(results: List[Dict], output_format: str = "all", 
                   output_dir: str = "reports") -> Dict:
    """
    Generate report in specified format(s)
    
    Args:
        results: List of test result dictionaries
        output_format: "html", "json", "all"
        output_dir: Directory to save reports
        
    Returns:
        Dictionary with paths to generated reports
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    generated = {}
    
    if output_format in ("json", "all"):
        json_path = f"{output_dir}/test_report.json"
        generate_json_report(results, json_path)
        generated["json"] = json_path
        print(f"📄 JSON Report: {json_path}")
    
    if output_format in ("html", "all"):
        html_path = f"{output_dir}/test_report.html"
        generate_html_report(results, html_path)
        generated["html"] = html_path
        print(f"🌐 HTML Report: {html_path}")
    
    return generated


def print_console_report(results: List[Dict]):
    """Print formatted report to console"""
    summary = calculate_summary(results)
    
    print("\n" + "=" * 80)
    print("📊 TEST EXECUTION REPORT")
    print("=" * 80)
    print(f"\n{'Metric':<20} {'Value':<10}")
    print("-" * 30)
    print(f"{'Total Tests':<20} {summary['total']:<10}")
    print(f"{'✅ Passed':<20} {summary['passed']:<10}")
    print(f"{'❌ Failed':<20} {summary['failed']:<10}")
    print(f"{'⏭️  Skipped':<20} {summary['skipped']:<10}")
    print(f"{'📈 Pass Rate':<20} {summary['pass_rate']:.1f}%")
    print("\n" + "=" * 80)
    print("📋 DETAILED RESULTS")
    print("=" * 80)
    
    for result in results:
        status_icon = "✅" if result.get("status") == "PASS" else "❌" if result.get("status") == "FAIL" else "⏭️"
        
        # Get user input
        details = result.get("details", {})
        user_input = result.get('user_input') or details.get('mobile') or details.get('email') or details.get('input') or details.get('number') or 'N/A'
        
        print(f"\n{status_icon} {result.get('tc_id', 'N/A')} - {result.get('description', 'No description')}")
        print(f"   Input: {user_input}")
        print(f"   Status: {result.get('status', 'SKIP')}")
        
        if result.get("error"):
            print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Demo with sample data
    sample_results = [
        {"tc_id": "TC-01", "description": "Navigate to Upstox", "status": "PASS", "details": {"message": "Success"}},
        {"tc_id": "TC-02", "description": "Click Sign In", "status": "PASS", "details": {"message": "Success"}},
        {"tc_id": "TC-03", "description": "Enter Mobile", "status": "PASS", "details": {"message": "Valid mobile"}},
        {"tc_id": "TC-04", "description": "Invalid Mobile", "status": "FAIL", "error": "Too short"},
    ]
    
    generate_report(sample_results, "all")
    print_console_report(sample_results)
