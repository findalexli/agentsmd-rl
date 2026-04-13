#!/bin/bash
# Gold patch for sample task: fix is_code_file to handle edge cases

cd /workspace/taskforge

# Apply fix using Python - more reliable than sed for multi-line edits
python3 << 'PYEOF'
import re

with open("taskforge/config.py", "r") as f:
    content = f.read()

# Find the is_code_file function and fix the bug
old_code = '''def is_code_file(path: str) -> bool:
    """Check if a file is a real code file (not docs/config/lockfile)."""
    if is_config_file(path):
        return False
    # BUG: Files without extension are incorrectly rejected
    if "." not in path:
        return False  # BUG: should return True for files like Makefile
    ext = "." + path.rsplit(".", 1)[-1]'''

new_code = '''def is_code_file(path: str) -> bool:
    """Check if a file is a real code file (not docs/config/lockfile)."""
    if is_config_file(path):
        return False
    # Handle edge case: paths without any extension
    if "." not in path:
        return True  # Files without extension are likely executable scripts
    ext = "." + path.rsplit(".", 1)[-1]'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open("taskforge/config.py", "w") as f:
        f.write(content)
    print("Patch applied successfully")
else:
    print("ERROR: Could not find target code to patch")
    exit(1)
PYEOF
