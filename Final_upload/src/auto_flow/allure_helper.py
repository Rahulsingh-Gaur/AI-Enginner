#!/usr/bin/env python3
"""
Allure Helper - Generates Allure result files
Extracted from auto_run_full_flow.py for better modularity
"""
import json
import uuid
import os
from datetime import datetime
from pathlib import Path


class AllureHelper:
    """Helper class to generate Allure result files"""

    def __init__(self, results_dir="reports/allure-results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.container_uuid = str(uuid.uuid4())
        self.test_uuid = str(uuid.uuid4())
        self.steps = []
        self.start_time = None
        self.attachments = []

    def start_test(self, name: str, description: str = ""):
        """Start test recording"""
        self.start_time = int(datetime.now().timestamp() * 1000)
        self.test_name = name
        self.test_description = description

    def add_step(self, name: str, status: str = "passed", details: dict = None):
        """Add a test step"""
        step_uuid = str(uuid.uuid4())
        step_data = {
            "uuid": step_uuid,
            "name": name,
            "status": status,
            "stage": "finished",
            "steps": [],
            "attachments": [],
            "parameters": [],
            "start": int(datetime.now().timestamp() * 1000),
            "stop": int(datetime.now().timestamp() * 1000)
        }
        if details:
            step_data["description"] = json.dumps(details, indent=2)
        self.steps.append(step_data)
        return step_uuid

    def add_attachment(self, name: str, content: str, attachment_type: str = "text/plain"):
        """Add attachment to test"""
        attach_uuid = str(uuid.uuid4())
        attach_file = self.results_dir / f"{attach_uuid}-attachment.txt"
        with open(attach_file, 'w') as f:
            f.write(content)

        self.attachments.append({
            "name": name,
            "source": f"{attach_uuid}-attachment.txt",
            "type": attachment_type
        })
        return attach_uuid

    def end_test(self, status: str = "passed", message: str = "", test_summary: dict = None):
        """End test and write Allure result files"""
        stop_time = int(datetime.now().timestamp() * 1000)

        # Create test result
        test_result = {
            "uuid": self.test_uuid,
            "historyId": self.test_name.replace(" ", "_"),
            "testCaseId": self.test_name.replace(" ", "_"),
            "fullName": f"auto_run_full_flow.{self.test_name.replace(' ', '_')}",
            "name": self.test_name,
            "description": self.test_description,
            "status": status,
            "stage": "finished",
            "steps": self.steps,
            "attachments": self.attachments,
            "parameters": [],
            "labels": [
                {"name": "feature", "value": "E2E Flow"},
                {"name": "story", "value": "5-Stage Authentication Flow"},
                {"name": "suite", "value": "Auto Run Full Flow"},
                {"name": "framework", "value": "pytest"},
                {"name": "language", "value": "python"},
                {"name": "host", "value": os.uname().nodename},
                {"name": "package", "value": "auto_run_full_flow"}
            ],
            "start": self.start_time,
            "stop": stop_time
        }

        # Add test summary as attachment if provided
        if test_summary:
            summary_content = self._format_summary(test_summary)
            self.add_attachment("📊 Test Summary", summary_content, "text/plain")
            self.add_attachment("Test Data (JSON)", json.dumps(test_summary, indent=2), "application/json")

        if message and status != "passed":
            test_result["statusDetails"] = {"message": message, "trace": ""}

        # Update attachments in test result
        test_result["attachments"] = self.attachments

        # Write test result file
        result_file = self.results_dir / f"{self.test_uuid}-result.json"
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)

        # Write container file
        container = {
            "uuid": self.container_uuid,
            "name": "Auto Run Full Flow",
            "children": [self.test_uuid],
            "befores": [],
            "afters": []
        }
        container_file = self.results_dir / f"{self.container_uuid}-container.json"
        with open(container_file, 'w') as f:
            json.dump(container, f, indent=2)

        return result_file

    def _format_summary(self, test_summary: dict) -> str:
        """Format test summary as readable text"""
        content = "🎯 TEST DATA SUMMARY\n"
        content += "=" * 50 + "\n\n"
        content += f"📱 Mobile Number:     {test_summary.get('mobile_number', 'N/A')}\n"
        content += f"📧 Email:             {test_summary.get('email', 'N/A')}\n"
        content += f"🆔 Profile ID:        {test_summary.get('profile_id', 'N/A')}\n"
        content += f"👤 User Type:         {test_summary.get('user_type', 'N/A')}\n"
        content += f"📊 Customer Status:   {test_summary.get('customer_status', 'N/A')}\n"
        content += f"🔗 Redirect URI:      {test_summary.get('redirect_uri', 'N/A')}\n"
        content += "\n" + "=" * 50 + "\n"
        return content
