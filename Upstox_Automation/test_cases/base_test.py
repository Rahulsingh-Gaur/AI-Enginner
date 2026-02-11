#!/usr/bin/env python3
"""
Base Test Case Class
Provides common functionality for all test cases
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class BaseTestCase:
    """Base class for all test cases"""
    
    def __init__(self, test_data_path: str = "config/test_data.json"):
        """
        Initialize base test case
        
        Args:
            test_data_path: Path to test data JSON file
        """
        self.test_data_path = test_data_path
        self.test_data = self._load_test_data()
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def _load_test_data(self) -> Dict:
        """Load test data from JSON file"""
        try:
            with open(self.test_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Test data file not found: {self.test_data_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing test data: {e}")
            return {}
    
    def log_result(self, tc_id: str, description: str, status: str, 
                   details: Dict = None, error: str = None) -> Dict:
        """
        Log a test result
        
        Args:
            tc_id: Test case ID
            description: Test case description
            status: PASS, FAIL, or SKIP
            details: Additional details dictionary
            error: Error message if failed
            
        Returns:
            Result dictionary
        """
        result = {
            "tc_id": tc_id,
            "description": description,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
            "error": error
        }
        self.results.append(result)
        return result
    
    def run_test(self, tc_id: str, description: str, test_func, *args, **kwargs) -> Dict:
        """
        Run a single test with error handling
        
        Args:
            tc_id: Test case ID
            description: Test case description
            test_func: Function to execute
            *args, **kwargs: Arguments to pass to test function
            
        Returns:
            Result dictionary
        """
        print(f"\n🧪 Running {tc_id}: {description}")
        
        try:
            self.start_time = time.time()
            result = test_func(*args, **kwargs)
            self.end_time = time.time()
            
            # If test_func returns a dict, merge it
            if isinstance(result, dict):
                result["execution_time"] = round(self.end_time - self.start_time, 2)
                self.log_result(tc_id, description, result.get("status", "PASS"), result)
            else:
                self.log_result(tc_id, description, "PASS", 
                              {"execution_time": round(self.end_time - self.start_time, 2)})
            
            print(f"✅ {tc_id} PASSED")
            
        except Exception as e:
            self.end_time = time.time()
            error_msg = str(e)
            self.log_result(tc_id, description, "FAIL", 
                          {"execution_time": round(self.end_time - self.start_time, 2)},
                          error_msg)
            print(f"❌ {tc_id} FAILED: {error_msg}")
        
        return self.results[-1]
    
    def get_results(self) -> List[Dict]:
        """Get all test results"""
        return self.results
    
    def get_summary(self) -> Dict:
        """Get test execution summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": round((passed / total * 100), 2) if total > 0 else 0
        }
    
    def print_summary(self):
        """Print test summary to console"""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests:  {summary['total']}")
        print(f"✅ Passed:    {summary['passed']}")
        print(f"❌ Failed:    {summary['failed']}")
        print(f"⏭️  Skipped:   {summary['skipped']}")
        print(f"📈 Pass Rate: {summary['pass_rate']}%")
        print("=" * 60)
