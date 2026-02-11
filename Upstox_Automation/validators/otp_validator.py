#!/usr/bin/env python3
"""
OTP Validator Module
Validates OTP (One Time Password) inputs
"""

from typing import Dict, List


def validate_otp(otp: str, expected_length: int = 6) -> Dict:
    """
    Validate OTP format
    
    Args:
        otp: OTP string to validate
        expected_length: Expected OTP length (default 6)
        
    Returns:
        Dict with keys:
        - valid: bool - Whether validation passed
        - errors: List[str] - List of error messages if any
        - formatted: str - Cleaned OTP if valid
    """
    result = {
        "valid": False,
        "errors": [],
        "formatted": None
    }
    
    # Check if empty
    if not otp or not str(otp).strip():
        result["errors"].append("OTP is empty")
        return result
    
    # Convert to string and strip whitespace
    otp_clean = str(otp).strip().replace(" ", "")
    
    # Check if numeric
    if not otp_clean.isdigit():
        result["errors"].append("OTP must contain only digits")
    
    # Check length
    if len(otp_clean) != expected_length:
        result["errors"].append(f"OTP must be {expected_length} digits (found {len(otp_clean)})")
    
    # Check for common invalid patterns
    if otp_clean == "0" * expected_length:
        result["errors"].append("OTP cannot be all zeros")
    
    if otp_clean == "1" * expected_length:
        result["errors"].append("OTP cannot be all same digits")
    
    # Sequential numbers check (123456, 654321)
    sequential_patterns = [
        "".join(str(i % 10) for i in range(expected_length)),
        "".join(str((expected_length - i) % 10) for i in range(1, expected_length + 1))
    ]
    if otp_clean in sequential_patterns:
        result["warnings"] = ["OTP appears to be sequential numbers"]
    
    # If no errors, mark as valid
    if not result["errors"]:
        result["valid"] = True
        result["formatted"] = otp_clean
    
    return result


def validate_otp_with_expiry(otp: str, timestamp_received: float, 
                             expiry_seconds: int = 300) -> Dict:
    """
    Validate OTP with expiry check
    
    Args:
        otp: OTP string to validate
        timestamp_received: Unix timestamp when OTP was received
        expiry_seconds: OTP expiry time in seconds (default 5 minutes)
        
    Returns:
        Dict with validation result including expiry status
    """
    import time
    
    result = validate_otp(otp)
    
    if result["valid"]:
        current_time = time.time()
        elapsed = current_time - timestamp_received
        
        if elapsed > expiry_seconds:
            result["valid"] = False
            result["errors"].append(f"OTP has expired (valid for {expiry_seconds} seconds)")
            result["expired"] = True
        else:
            result["expired"] = False
            result["remaining_seconds"] = expiry_seconds - elapsed
    
    return result


def validate_multiple_otps(otps: List[str], expected_length: int = 6) -> List[Dict]:
    """
    Validate multiple OTPs
    
    Args:
        otps: List of OTP strings
        expected_length: Expected OTP length
        
    Returns:
        List of validation result dictionaries
    """
    return [validate_otp(o, expected_length) for o in otps]


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


def generate_otp_mask(otp: str, visible_chars: int = 2) -> str:
    """
    Generate masked version of OTP for logging/display
    
    Args:
        otp: OTP string
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked OTP string (e.g., "12****56")
    """
    if len(otp) <= visible_chars * 2:
        return "*" * len(otp)
    
    return otp[:visible_chars] + "*" * (len(otp) - visible_chars * 2) + otp[-visible_chars:]


if __name__ == "__main__":
    # Test the validator
    test_otps = [
        "123456",
        "12345",
        "1234567",
        "abcdef",
        "",
        "000000",
        "111111",
        "654321"
    ]
    
    print("OTP Validator Test Results:")
    print("=" * 50)
    for otp in test_otps:
        result = validate_otp(otp)
        status = "✅ PASS" if result["valid"] else "❌ FAIL"
        print(f"\n{status} | Input: '{otp}'")
        if result["errors"]:
            print(f"   Errors: {', '.join(result['errors'])}")
        else:
            print(f"   Formatted: {result['formatted']}")
            print(f"   Masked: {generate_otp_mask(result['formatted'])}")
