#!/bin/bash
set -e

cd /workspace/kotlin

cursor_file="compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt"

# Create a Python script to check if fix is already applied and verify the fix
cat > /tmp/check_fix.py << 'PYEOF'
import sys

with open("compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt", "r") as f:
    content = f.read()

# Find validIdentifierWithDotRegex section
idx = content.find("val validIdentifierWithDotRegex")
if idx < 0:
    print("ERROR: Could not find validIdentifierWithDotRegex", file=sys.stderr)
    sys.exit(1)

section = content[idx:idx+500]

# Check if fix is already applied
if "(?!\\.\\.\\.)" in section:
    print("Fix already applied")
    sys.exit(0)

print("Fix not yet applied")
sys.exit(1)
PYEOF

if python3 /tmp/check_fix.py 2>/dev/null; then
    exit 0
fi

# Create a Python script file and run it to apply the fix
cat > /tmp/apply_fix.py << 'PYEOF'
import sys
import re

with open("compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt", "r") as f:
    content = f.read()

# Find the validIdentifierWithDotRegex section
idx = content.find("val validIdentifierWithDotRegex")
if idx < 0:
    print("ERROR: Could not find marker", file=sys.stderr)
    sys.exit(1)

# Get the section
section = content[idx:idx+600]

# Find the regex line (starts with spaces and ^((=)
match = re.search(r"^(\s+)(\^\(\(=.*?\]\)\+\))$", section, re.MULTILINE)
if not match:
    print("ERROR: Could not find regex line", file=sys.stderr)
    sys.exit(1)

indent = match.group(1)
old_pattern = match.group(2)

# Transform:
# ^((= -> ^((?!\.\.\.)(=
# ])+) -> ])))+
new_pattern = old_pattern.replace("^((=", "^((?!\.\.\.)(=")
new_pattern = new_pattern.replace("]+)", "])))+")

print(f"Old: {repr(old_pattern)}")
print(f"New: {repr(new_pattern)}")

if new_pattern == old_pattern:
    print("ERROR: Pattern unchanged", file=sys.stderr)
    sys.exit(1)

# Replace in content
old_full = indent + old_pattern
new_full = indent + new_pattern
content = content.replace(old_full, new_full, 1)

with open("compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt", "w") as f:
    f.write(content)

print("Fix applied")
PYEOF

python3 /tmp/apply_fix.py

# Verify the fix is in validIdentifierWithDotRegex
cat > /tmp/verify_fix.py << 'PYEOF'
import sys

with open("compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt", "r") as f:
    content = f.read()

idx = content.find("val validIdentifierWithDotRegex")
if idx < 0:
    print("ERROR: validIdentifierWithDotRegex not found", file=sys.stderr)
    sys.exit(1)

section = content[idx:idx+500]

if "(?!\\.\\.\\.)" not in section:
    print("ERROR: Fix verification failed - negative lookahead not in validIdentifierWithDotRegex", file=sys.stderr)
    print(section, file=sys.stderr)
    sys.exit(1)

print("Fix verified")
PYEOF

python3 /tmp/verify_fix.py
