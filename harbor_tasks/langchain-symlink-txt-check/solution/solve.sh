#!/bin/bash
set -e

cd /workspace/langchain

# Apply the security fix using Python for reliable editing
python3 << 'PYEOF'
import re

filepath = "libs/core/langchain_core/prompts/loading.py"

with open(filepath, 'r') as f:
    content = f.read()

# The fix: resolve symlinks before checking file extension
# Find and replace the vulnerable pattern
old_code = '''        if not allow_dangerous_paths:
            _validate_path(template_path)
        # Load the template.
        if template_path.suffix == ".txt":
            template = template_path.read_text(encoding="utf-8")'''

new_code = '''        if not allow_dangerous_paths:
            _validate_path(template_path)
        # Resolve symlinks before checking the suffix so that a symlink named
        # "exploit.txt" pointing to a non-.txt file is caught.
        resolved_path = template_path.resolve()
        # Load the template.
        if resolved_path.suffix == ".txt":
            template = resolved_path.read_text(encoding="utf-8")'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Patch applied successfully")
else:
    print("ERROR: Could not find the expected code pattern to patch")
    print("Searching for partial match...")
    if "template_path.suffix" in content:
        print("Found template_path.suffix in file")
    else:
        print("template_path.suffix not found")
    exit(1)
PYEOF

# Verify the patch was applied by checking for the distinctive line
grep -q "resolved_path = template_path.resolve()" \
    libs/core/langchain_core/prompts/loading.py \
    && echo "Verification passed: resolved_path found" \
    || (echo "Verification failed: resolved_path not found" && exit 1)
