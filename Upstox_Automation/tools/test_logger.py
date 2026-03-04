#!/usr/bin/env python3
"""
Test Logger Module
Captures all test execution logs and generates Logs.md
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class TestLogger:
    """Logger for test execution"""
    
    def __init__(self, test_name: str = "Test"):
        self.test_name = test_name
        self.logs = []
        self.start_time = datetime.now()
        self.session_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        
    def log_step(self, step_number: int, title: str, status: str, details: Dict = None):
        """Log a test step"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step_number": step_number,
            "title": title,
            "status": status,
            "details": details or {}
        }
        self.logs.append(log_entry)
        return log_entry
    
    def log_input(self, field_name: str, value: str, masked: bool = False):
        """Log user input"""
        display_value = "*****" if masked else value
        self.log_step(
            step_number=len(self.logs) + 1,
            title=f"INPUT: {field_name}",
            status="INFO",
            details={
                "field": field_name,
                "value": display_value,
                "masked": masked,
                "type": "user_input"
            }
        )
    
    def log_output(self, title: str, message: str, data: Dict = None):
        """Log system output"""
        self.log_step(
            step_number=len(self.logs) + 1,
            title=f"OUTPUT: {title}",
            status="INFO",
            details={
                "message": message,
                "data": data or {},
                "type": "system_output"
            }
        )
    
    def log_otp_prompt(self, mobile_number: str):
        """Log OTP prompt for manual entry"""
        self.log_step(
            step_number=len(self.logs) + 1,
            title="OTP REQUIRED",
            status="MANUAL",
            details={
                "mobile": mobile_number,
                "message": f"Please enter OTP sent to {mobile_number}",
                "action_required": "Manual OTP entry",
                "type": "manual_intervention"
            }
        )
    
    def log_error(self, error_message: str, exception: str = None):
        """Log error"""
        self.log_step(
            step_number=len(self.logs) + 1,
            title="ERROR",
            status="FAIL",
            details={
                "error": error_message,
                "exception": exception,
                "type": "error"
            }
        )
    
    def log_screenshot(self, screenshot_path: str, description: str = ""):
        """Log screenshot capture"""
        self.log_step(
            step_number=len(self.logs) + 1,
            title="SCREENSHOT",
            status="INFO",
            details={
                "path": screenshot_path,
                "description": description,
                "type": "screenshot"
            }
        )
    
    def generate_logs_md(self, output_path: str = "Logs.md") -> str:
        """Generate Logs.md file"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        md_content = f"""# Test Execution Log

## Session Information

| Field | Value |
|-------|-------|
| **Test Name** | {self.test_name} |
| **Session ID** | {self.session_id} |
| **Start Time** | {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} |
| **End Time** | {end_time.strftime('%Y-%m-%d %H:%M:%S')} |
| **Duration** | {duration:.2f} seconds |

## Execution Steps

"""
        
        for log in self.logs:
            step_num = log.get("step_number", 0)
            title = log.get("title", "Unknown")
            status = log.get("status", "INFO")
            timestamp = log.get("timestamp", "")
            details = log.get("details", {})
            
            # Status icon
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️" if status == "MANUAL" else "ℹ️"
            
            md_content += f"### Step {step_num}: {title}\n\n"
            md_content += f"**Status:** {status_icon} {status}  \n"
            md_content += f"**Time:** {timestamp}  \n\n"
            
            # Add details based on type
            log_type = details.get("type", "")
            
            if log_type == "user_input":
                field = details.get("field", "")
                value = details.get("value", "")
                masked = details.get("masked", False)
                md_content += f"**Field:** `{field}`  \n"
                md_content += f"**Value:** `{value}` {'(masked)' if masked else ''}  \n\n"
                
            elif log_type == "system_output":
                message = details.get("message", "")
                data = details.get("data", {})
                md_content += f"**Message:** {message}  \n"
                if data:
                    md_content += f"**Data:**\n```json\n{json.dumps(data, indent=2)}\n```\n\n"
                    
            elif log_type == "manual_intervention":
                mobile = details.get("mobile", "")
                message = details.get("message", "")
                action = details.get("action_required", "")
                md_content += f"**Mobile:** `{mobile}`  \n"
                md_content += f"**Message:** {message}  \n"
                md_content += f"**Action Required:** ⚠️ {action}  \n\n"
                
            elif log_type == "error":
                error_msg = details.get("error", "")
                exception = details.get("exception", "")
                md_content += f"**Error:** ❌ {error_msg}  \n"
                if exception:
                    md_content += f"**Exception:**\n```\n{exception}\n```\n\n"
                    
            elif log_type == "screenshot":
                path = details.get("path", "")
                desc = details.get("description", "")
                md_content += f"**Screenshot:** `{path}`  \n"
                if desc:
                    md_content += f"**Description:** {desc}  \n\n"
            else:
                # Generic details
                if details:
                    md_content += f"**Details:**\n```json\n{json.dumps(details, indent=2)}\n```\n\n"
            
            md_content += "---\n\n"
        
        # Summary section
        total_steps = len(self.logs)
        passed = sum(1 for log in self.logs if log.get("status") == "PASS")
        failed = sum(1 for log in self.logs if log.get("status") == "FAIL")
        manual = sum(1 for log in self.logs if log.get("status") == "MANUAL")
        
        md_content += f"""## Summary

| Metric | Count |
|--------|-------|
| **Total Steps** | {total_steps} |
| **Passed** | {passed} ✅ |
| **Failed** | {failed} ❌ |
| **Manual Intervention** | {manual} ⚠️ |
| **Duration** | {duration:.2f} seconds |

## Notes

- **Input:** User input fields captured with actual values (masked for sensitive data)
- **Output:** System responses and page states
- **Manual:** Steps requiring human intervention (e.g., OTP entry)
- **Screenshots:** Visual captures of key steps (if enabled)

---
*Auto-generated on {end_time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Write to file
        Path(output_path).write_text(md_content)
        return output_path
    
    def generate_json_log(self, output_path: str = "logs.json") -> str:
        """Generate JSON log file"""
        log_data = {
            "test_name": self.test_name,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "logs": self.logs
        }
        
        with open(output_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return output_path


if __name__ == "__main__":
    # Demo
    logger = TestLogger("Happy Path Test")
    
    logger.log_input("Mobile Number", "9552931377")
    logger.log_output("Navigation", "Navigated to upstox.com", {"url": "https://upstox.com/"})
    logger.log_otp_prompt("9552931377")
    logger.log_input("OTP", "123456", masked=True)
    logger.log_output("Result", "Login successful", {"status": "PASS"})
    
    logger.generate_logs_md("Logs.md")
    logger.generate_json_log("logs.json")
    
    print("✅ Logs generated: Logs.md, logs.json")
