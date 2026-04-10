#!/usr/bin/env python
"""Quick test of check_docstrings basic functionality"""
import sys
import os
sys.path.insert(0, "utils")
from check_docstrings import get_default_description, replace_default_in_arg_description
import inspect

# Test 1: replace_default_in_arg_description
desc = "`float`, *optional*, defaults to 2.0"
result = replace_default_in_arg_description(desc, 2.0)
assert result == "`float`, *optional*, defaults to 2.0", f"Test 1a failed: {result}"

result = replace_default_in_arg_description(desc, 1.0)
assert result == "`float`, *optional*, defaults to 1.0", f"Test 1b failed: {result}"

# Test 2: get_default_description
def _fake(a, b: int, c=1, d: float = 2.0):
    pass

params = inspect.signature(_fake).parameters
assert get_default_description(params["a"]) == "`<fill_type>`", "Test 2a failed"
assert get_default_description(params["b"]) == "`int`", "Test 2b failed"

print("All basic repo_utils tests passed!")
