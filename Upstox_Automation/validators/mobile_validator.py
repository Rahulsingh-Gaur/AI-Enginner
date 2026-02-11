#!/usr/bin/env python3
"""
Mobile Number Validator Module
Validates mobile numbers according to Indian mobile number rules
"""

import re
from typing import Dict, List


def validate_mobile(mobile: str) -> Dict:
    """
    Validate mobile number format
    
    Args:
        mobile: Mobile number string to validate
        
    Returns:
        Dict with keys:
        - valid: bool - Whether validation passed
        - errors: List[str] - List of error messages if any
        - formatted: str - Cleaned mobile number if valid
    """
    result = {
        "valid": False,
        "errors": [],
        "formatted": None
    }
    
    # Check if empty
    if not mobile or not str(mobile).strip():
        result["errors"].append("Mobile number is empty")
        return result
    
    # Convert to string and remove any spaces/dashes
    mobile_clean = str(mobile).strip().replace(" ", "").replace("-", "").replace("+", "")
    
    # Remove country code if present (91)
    if mobile_clean.startswith("91") and len(mobile_clean) == 12:
        mobile_clean = mobile_clean[2:]
    
    # Check length
    if len(mobile_clean) != 10:
        result["errors"].append(f"Mobile number must be 10 digits (found {len(mobile_clean)})")
    
    # Check if numeric
    if not mobile_clean.isdigit():
        result["errors"].append("Mobile number must contain only digits")
    
    # Check valid starting digit (Indian mobile numbers start with 6, 7, 8, or 9)
    if mobile_clean and mobile_clean[0] not in '6789':
        result["errors"].append("Invalid mobile number - must start with 6, 7, 8, or 9")
    
    # If no errors, mark as valid
    if not result["errors"]:
        result["valid"] = True
        result["formatted"] = mobile_clean
    
    return result


def validate_multiple_mobiles(mobiles: List[str]) -> List[Dict]:
    """
    Validate multiple mobile numbers
    
    Args:
        mobiles: List of mobile number strings
        
    Returns:
        List of validation result dictionaries
    """
    return [validate_mobile(m) for m in mobiles]


def get_validation_summary(results: List[Dict]) -> Dict:
    """
    Get summary of validation results
    
    Args:
        results: List of validation result dictionaries
        
    Returns:
        Summary dictionary with pass/fail counts
    """
    total = len(results)
    passed = sum(1 for r in results if r["valid"])
    failed = total - passed
    
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": (passed / total * 100) if total > 0 else 0
    }


# =============================================================================
# MOBILE NUMBER TEST CASES - SINGLE SOURCE OF TRUTH
# All mobile number test inputs are defined here
# Other files should import from this module
# =============================================================================

MOBILE_TEST_CASES = {
    "valid": [
        {
            "number": "9552931377",
            "description": "Valid 10-digit mobile number starting with 9",
            "expected": "PASS"
        },
        {
            "number": "8976258876",
            "description": "Valid 10-digit mobile number starting with 8",
            "expected": "PASS"
        },
        {
            "number": "7552931377",
            "description": "Valid 10-digit mobile number starting with 7",
            "expected": "PASS"
        },
        {
            "number": "6552931377",
            "description": "Valid 10-digit mobile number starting with 6",
            "expected": "PASS"
        }
    ],
    "invalid": [
        {
            "number": "1111111111",
            "description": "10 digits but starts with 1 (should show error: Make sure your mobile number was entered correctly)",
            "expected": "FAIL",
            "error_message": "Make sure your mobile number was entered correctly"
        },
        {
            "number": "2345678888",
            "description": "10 digits but starts with 2 (should show error: Make sure your mobile number was entered correctly)",
            "expected": "FAIL",
            "error_message": "Make sure your mobile number was entered correctly"
        },
        {
            "number": "3456788888",
            "description": "10 digits but starts with 3 (0-5 series invalid)",
            "expected": "FAIL",
            "error_message": "Make sure your mobile number was entered correctly"
        },
        {
            "number": "4567899999",
            "description": "10 digits but starts with 4 (0-5 series invalid)",
            "expected": "FAIL",
            "error_message": "Make sure your mobile number was entered correctly"
        },
        {
            "number": "5567899999",
            "description": "10 digits but starts with 5 (0-5 series invalid)",
            "expected": "FAIL",
            "error_message": "Make sure your mobile number was entered correctly"
        },
        {
            "number": "0123456789",
            "description": "10 digits but starts with 0 (0-5 series invalid)",
            "expected": "FAIL",
            "error_message": "Make sure your mobile number was entered correctly"
        },
        {
            "number": "12345",
            "description": "Less than 10 digits",
            "expected": "FAIL",
            "error_message": "Mobile number must be 10 digits"
        },
        {
            "number": "12345678901",
            "description": "More than 10 digits",
            "expected": "FAIL",
            "error_message": "Mobile number must be 10 digits"
        },
        {
            "number": "abcdefghij",
            "description": "Non-numeric characters only",
            "expected": "FAIL",
            "error_message": "Mobile number must contain only digits"
        },
        {
            "number": "95529h31377",
            "description": "Contains invalid character in middle",
            "expected": "FAIL",
            "error_message": "Mobile number must contain only digits"
        },
        {
            "number": "",
            "description": "Empty mobile number",
            "expected": "FAIL",
            "error_message": "Mobile number is empty"
        },
        {
            "number": "1234567890",
            "description": "10 digits, starts with 1 (0-5 series)",
            "expected": "FAIL",
            "error_message": "Make sure your mobile number was entered correctly"
        }
    ]
}


def get_mobile_test_cases(category: str = "all") -> list:
    """
    Get mobile number test cases
    
    Args:
        category: "all", "valid", or "invalid"
        
    Returns:
        List of test case dictionaries
    """
    if category == "valid":
        return MOBILE_TEST_CASES["valid"]
    elif category == "invalid":
        return MOBILE_TEST_CASES["invalid"]
    else:
        return MOBILE_TEST_CASES["valid"] + MOBILE_TEST_CASES["invalid"]


def get_mobile_numbers_list(category: str = "all") -> list:
    """
    Get list of mobile numbers only (for simple use cases)
    
    Args:
        category: "all", "valid", or "invalid"
        
    Returns:
        List of mobile number strings
    """
    cases = get_mobile_test_cases(category)
    return [case["number"] for case in cases]


def get_mobile_numbers_for_browser_test() -> list:
    """
    Get mobile numbers formatted for browser automation testing
    Returns list of tuples: (mobile_number, expected_result)
    """
    test_cases = []
    
    # Valid numbers - should PASS (go to OTP screen)
    for case in MOBILE_TEST_CASES["valid"]:
        test_cases.append((case["number"], "PASS"))
    
    # Invalid numbers - should FAIL (show error message)
    for case in MOBILE_TEST_CASES["invalid"]:
        test_cases.append((case["number"], "FAIL"))
    
    return test_cases


# Default mobile number for automation
DEFAULT_MOBILE_NUMBER = "9552931377"


if __name__ == "__main__":
    # Test the validator with all test cases
    print("=" * 70)
    print("📱 MOBILE VALIDATOR - TESTING ALL CASES")
    print("=" * 70)
    
    all_cases = get_mobile_test_cases("all")
    
    print(f"\n🧪 Total Test Cases: {len(all_cases)}")
    print(f"   ✅ Valid: {len(MOBILE_TEST_CASES['valid'])}")
    print(f"   ❌ Invalid: {len(MOBILE_TEST_CASES['invalid'])}")
    print("\n" + "=" * 70)
    
    passed = 0
    failed = 0
    
    for case in all_cases:
        number = case["number"]
        expected = case["expected"]
        description = case["description"]
        
        result = validate_mobile(number)
        actual = "PASS" if result["valid"] else "FAIL"
        test_passed = (actual == expected)
        
        status_icon = "✅" if test_passed else "❌"
        status_text = "PASS" if test_passed else "FAIL"
        
        print(f"\n{status_icon} [{status_text}] Input: '{number}'")
        print(f"   Description: {description}")
        print(f"   Expected: {expected} | Actual: {actual}")
        
        if result["errors"]:
            print(f"   Errors: {', '.join(result['errors'])}")
        else:
            print(f"   Formatted: {result['formatted']}")
        
        if test_passed:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Total: {len(all_cases)} | ✅ Passed: {passed} | ❌ Failed: {failed}")
    print(f"Pass Rate: {(passed/len(all_cases)*100):.1f}%" if all_cases else "N/A")
    print("=" * 70)
