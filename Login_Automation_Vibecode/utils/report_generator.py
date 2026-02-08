"""
Test Report Generator - Generates execution reports and bug reports.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Data class to store test result information."""
    test_name: str
    test_file: str
    status: str  # PASSED, FAILED, SKIPPED, ERROR
    duration: float
    timestamp: str
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    screenshot_path: Optional[str] = None
    video_path: Optional[str] = None
    traceback: Optional[str] = None
    browser: str = settings.BROWSER
    url: str = ""
    markers: List[str] = field(default_factory=list)
    description: str = ""
    steps: List[str] = field(default_factory=list)


@dataclass
class TestExecutionSummary:
    """Data class for test execution summary."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    start_time: str = ""
    end_time: str = ""
    duration: float = 0.0
    browser: str = settings.BROWSER
    base_url: str = settings.BASE_URL


class ReportGenerator:
    """Generates test execution reports and bug reports."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.summary = TestExecutionSummary()
        self.report_dir = Path(settings.REPORT_DIR)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.start_time: Optional[datetime] = None
        
    def start_execution(self):
        """Mark the start of test execution."""
        self.start_time = datetime.now()
        self.summary.start_time = self.start_time.isoformat()
        logger.info(f"Test execution started at {self.summary.start_time}")
    
    def add_result(self, result: TestResult):
        """Add a test result to the collection."""
        self.results.append(result)
        self.summary.total_tests += 1
        
        if result.status == "PASSED":
            self.summary.passed += 1
        elif result.status == "FAILED":
            self.summary.failed += 1
        elif result.status == "SKIPPED":
            self.summary.skipped += 1
        else:
            self.summary.errors += 1
            
        logger.info(f"Test '{result.test_name}' - {result.status}")
    
    def finish_execution(self):
        """Mark the end of test execution and generate reports."""
        end_time = datetime.now()
        self.summary.end_time = end_time.isoformat()
        
        if self.start_time:
            self.summary.duration = (end_time - self.start_time).total_seconds()
        
        logger.info(f"Test execution finished. Duration: {self.summary.duration:.2f}s")
        
        # Generate all reports
        self._generate_markdown_report()
        self._generate_simple_bug_report()
    
    def _generate_markdown_report(self):
        """Generate simplified Markdown test execution report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.report_dir / f"TestExecutionReport_{timestamp}.md"
        
        md_content = f"""# Test Execution Report

## Summary

| Metric | Value |
|--------|-------|
| **Start Time** | {self.summary.start_time} |
| **End Time** | {self.summary.end_time} |
| **Duration** | {self.summary.duration:.2f} seconds |
| **Browser** | {self.summary.browser} |
| **Base URL** | {self.summary.base_url} |

## Test Results

| Status | Count |
|--------|-------|
| ✅ **Passed** | {self.summary.passed} |
| ❌ **Failed** | {self.summary.failed} |
| ⚠️ **Skipped** | {self.summary.skipped} |
| **Total** | {self.summary.total_tests} |

"""
        
        # Failed tests first
        failed_tests = [r for r in self.results if r.status == "FAILED"]
        if failed_tests:
            md_content += "## ❌ Failed Tests\n\n"
            for result in failed_tests:
                md_content += self._format_failed_test(result)
        
        # Passed tests
        passed_tests = [r for r in self.results if r.status == "PASSED"]
        if passed_tests:
            md_content += "## ✅ Passed Tests\n\n"
            for result in passed_tests:
                md_content += f"- **{result.test_name}** ({result.duration:.2f}s)\n"
            md_content += "\n"
        
        # Skipped tests
        skipped_tests = [r for r in self.results if r.status == "SKIPPED"]
        if skipped_tests:
            md_content += "## ⚠️ Skipped Tests\n\n"
            for result in skipped_tests:
                md_content += f"- **{result.test_name}**\n"
            md_content += "\n"
        
        md_content += f"""---
*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        with open(report_path, 'w') as f:
            f.write(md_content)
        
        logger.info(f"Report generated: {report_path}")
        return str(report_path)
    
    def _format_failed_test(self, result: TestResult) -> str:
        """Format a failed test for the report."""
        md = f"""### {result.test_name}

**Status:** ❌ FAILED  
**Duration:** {result.duration:.2f}s  
**Time:** {result.timestamp}

**Description:**
{result.description or 'No description available.'}

**Error:**
```
{result.error_message or 'No error message available.'}
```

"""
        if result.screenshot_path:
            md += f"**Screenshot:** `{result.screenshot_path}`\n\n"
        
        md += "---\n\n"
        return md
    
    def _generate_simple_bug_report(self):
        """Generate simplified BugReport.md in table format."""
        failed_tests = [r for r in self.results if r.status == "FAILED"]
        
        report_path = self.report_dir / "BugReport.md"
        
        bug_report = f"""# Bug Report - Failed Test Cases

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Failed:** {len(failed_tests)}  
**URL:** {settings.BASE_URL}

---

"""
        
        if not failed_tests:
            bug_report += "✅ All tests passed! No bugs to report.\n"
        else:
            # Summary table
            bug_report += "## Failed Tests Summary\n\n"
            bug_report += "| # | Test Case | Error | Screenshot |\n"
            bug_report += "|---|-----------|-------|------------|\n"
            
            for i, result in enumerate(failed_tests, 1):
                error_short = (result.error_message or "No error")[:50] + "..." if len(result.error_message or "") > 50 else (result.error_message or "No error")
                screenshot = "Yes" if result.screenshot_path else "No"
                bug_report += f"| {i} | {result.test_name} | {error_short} | {screenshot} |\n"
            
            bug_report += "\n---\n\n"
            
            # Detailed bug info
            for i, result in enumerate(failed_tests, 1):
                bug_report += f"""## Bug #{i}: {result.test_name}

### Test Details
| Field | Value |
|-------|-------|
| **Test ID** | {result.test_name} |
| **Status** | ❌ FAILED |
| **Duration** | {result.duration:.2f}s |
| **Browser** | {result.browser} |
| **URL** | {settings.BASE_URL} |

### Description
{result.description or 'No description available.'}

### Expected vs Actual
| Expected | Actual |
|----------|--------|
| Test should pass | Test FAILED |

### Error Message
```
{result.error_message or 'No error message'}
```

### Steps to Reproduce
1. Navigate to {settings.BASE_URL}
2. Execute test: {result.test_name}
3. Observe the failure

"""
                if result.screenshot_path:
                    bug_report += f"### Screenshot\n`{result.screenshot_path}`\n\n"
                
                bug_report += "---\n\n"
        
        bug_report += """*Auto-generated Bug Report*
"""
        
        with open(report_path, 'w') as f:
            f.write(bug_report)
        
        logger.info(f"Bug report generated: {report_path}")
        return str(report_path)


# Global report generator instance
report_generator = ReportGenerator()
