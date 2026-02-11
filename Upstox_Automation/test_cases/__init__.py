"""
Test Cases package for Upstox Automation
Contains test case classes for different flows
"""

from .base_test import BaseTestCase
from .test_login_flow import TestLoginFlow
from .test_email_flow import TestEmailFlow

__all__ = ['BaseTestCase', 'TestLoginFlow', 'TestEmailFlow']
