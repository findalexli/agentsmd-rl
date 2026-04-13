#!/bin/bash
# Gold fix: Correct the normalize_whitespace function

set -e

cd /workspace/repo

# Fix the bug: use .split() without arguments to handle all whitespace
cat > string_utils.py << 'EOF'
# String utility module - FIXED VERSION

def normalize_whitespace(text):
    """Normalize whitespace in text - collapses multiple whitespace chars to single space."""
    # FIXED: Using .split() without arguments handles all whitespace (spaces, tabs, newlines)
    return " ".join(text.split())

def to_title_case(text):
    """Convert string to title case (first letter of each word uppercase)."""
    return text.title()
EOF

echo "Fix applied successfully"
