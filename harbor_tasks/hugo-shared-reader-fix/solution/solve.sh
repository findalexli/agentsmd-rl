#!/bin/bash
set -e

cd /workspace/hugo

# Check if already applied (idempotency)
if grep -q "hugio.NewReadSeekerNoOpCloserFromString(content)" resources/page/pagemeta/page_frontmatter.go 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix using Python (more reliable than sed for multi-line changes)
python3 << 'PYEOF'
import re

file_path = "/workspace/hugo/resources/page/pagemeta/page_frontmatter.go"

with open(file_path, 'r') as f:
    content = f.read()

# Check if already applied
if 'content := s.ValueAsString()' in content:
    print("Patch already applied, skipping")
    exit(0)

# The pattern to replace - match the buggy implementation
old_pattern = r'return hugio\.NewOpenReadSeekCloser\(hugio\.NewReadSeekerNoOpCloserFromString\(s\.ValueAsString\(\)\)\)'

# The new code - each call returns a new independent reader
new_code = '''content := s.ValueAsString()
\treturn func() (hugio.ReadSeekCloser, error) {
\t\treturn hugio.NewReadSeekerNoOpCloserFromString(content), nil
\t}'''

if not re.search(old_pattern, content):
    print("ERROR: Could not find the pattern to replace")
    exit(1)

content = re.sub(old_pattern, new_code, content)

with open(file_path, 'w') as f:
    f.write(content)

print("Patch applied successfully")
PYEOF

echo "Fix applied"
