#!/bin/bash
# Gold solution patch for the task
# This demonstrates a fix for a syntax error in utils.py

cat << 'EOF' > /workspace/example-repo/src/utils.py
"""Utility functions for the example repo."""

def helper_function(x):
    """A helper that does something useful."""
    return x * 2

def process_data(items):
    """Process a list of items."""
    results = []
    for item in items:
        # Fixed: was missing colon in for loop
        results.append(helper_function(item))
    return results
EOF

echo "Fix applied successfully"
