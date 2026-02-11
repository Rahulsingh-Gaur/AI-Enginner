#!/usr/bin/env python3
"""
Email Validator Module
Validates email addresses according to standard email format rules
"""

import re
from typing import Dict, List


# Regular expression for email validation
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Pattern for consecutive dots
CONSECUTIVE_DOTS_REGEX = re.compile(r'\.\.+')


def validate_email(email: str) -> Dict:
    """
    Validate email address format
    
    Args:
        email: Email address string to validate
        
    Returns:
        Dict with keys:
        - valid: bool - Whether validation passed
        - errors: List[str] - List of error messages if any
        - normalized: str - Normalized email if valid
        - domain: str - Extracted domain if valid
    """
    result = {
        "valid": False,
        "errors": [],
        "normalized": None,
        "domain": None
    }
    
    # Check if empty
    if not email or not str(email).strip():
        result["errors"].append("Email is empty")
        return result
    
    # Strip whitespace
    email_clean = str(email).strip()
    
    # Check length
    if len(email_clean) > 254:
        result["errors"].append("Email is too long (max 254 characters)")
    
    # Check for @ symbol
    if '@' not in email_clean:
        result["errors"].append("Invalid email format - missing @ symbol")
        return result
    
    # Split local and domain parts
    parts = email_clean.split('@')
    if len(parts) != 2:
        result["errors"].append("Invalid email format - multiple @ symbols")
        return result
    
    local_part, domain_part = parts
    
    # Validate local part (before @)
    if not local_part:
        result["errors"].append("Invalid email format - missing local part (before @)")
    elif len(local_part) > 64:
        result["errors"].append("Local part is too long (max 64 characters)")
    elif local_part.startswith('.') or local_part.endswith('.'):
        result["errors"].append("Local part cannot start or end with a dot")
    elif CONSECUTIVE_DOTS_REGEX.search(local_part):
        result["errors"].append("Local part cannot contain consecutive dots")
    
    # Validate domain part (after @)
    if not domain_part:
        result["errors"].append("Invalid email format - missing domain part (after @)")
    elif '.' not in domain_part:
        result["errors"].append("Invalid email format - missing TLD (e.g., .com, .in)")
    elif domain_part.startswith('.') or domain_part.endswith('.'):
        result["errors"].append("Domain part cannot start or end with a dot")
    elif CONSECUTIVE_DOTS_REGEX.search(domain_part):
        result["errors"].append("Domain part cannot contain consecutive dots")
    
    # Check with regex pattern
    if not EMAIL_REGEX.match(email_clean):
        if not result["errors"]:  # Only add if no specific error already added
            result["errors"].append("Invalid email format")
    
    # If no errors, mark as valid
    if not result["errors"]:
        result["valid"] = True
        result["normalized"] = email_clean.lower()
        result["domain"] = domain_part.lower()
    
    return result


def validate_multiple_emails(emails: List[str]) -> List[Dict]:
    """
    Validate multiple email addresses
    
    Args:
        emails: List of email address strings
        
    Returns:
        List of validation result dictionaries
    """
    return [validate_email(e) for e in emails]


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


def is_corporate_email(email: str, allowed_domains: List[str] = None) -> bool:
    """
    Check if email is from allowed corporate domains
    
    Args:
        email: Email address to check
        allowed_domains: List of allowed corporate domains (e.g., ['rksv.in', 'upstox.com'])
        
    Returns:
        bool: True if email is from allowed domain
    """
    if allowed_domains is None:
        allowed_domains = ['rksv.in', 'upstox.com']
    
    result = validate_email(email)
    if not result["valid"]:
        return False
    
    return any(result["domain"].endswith(domain) for domain in allowed_domains)


if __name__ == "__main__":
    # Test the validator
    test_emails = [
        "Rahul.hajari@rksv.in",
        "test@",
        "@rksv.in",
        "test@domain",
        "",
        "test..user@rksv.in",
        "valid.user@example.com"
    ]
    
    print("Email Validator Test Results:")
    print("=" * 50)
    for email in test_emails:
        result = validate_email(email)
        status = "✅ PASS" if result["valid"] else "❌ FAIL"
        print(f"\n{status} | Input: '{email}'")
        if result["errors"]:
            print(f"   Errors: {', '.join(result['errors'])}")
        else:
            print(f"   Normalized: {result['normalized']}")
            print(f"   Domain: {result['domain']}")
