"""
Test Suite Package
Contains Happy Path and Regression tests
"""

from .happy_path_test import run_happy_path_test
from .regression_test import run_regression_test

__all__ = ['run_happy_path_test', 'run_regression_test']
