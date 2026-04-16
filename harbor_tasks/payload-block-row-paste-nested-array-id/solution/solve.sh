#!/bin/bash
set -e

cd /workspace/payload

# Use python to do the replacement reliably
python3 << 'PYEOF'
file_path = 'packages/ui/src/elements/ClipboardAction/mergeFormStateFromClipboard.ts'
with open(file_path, 'r') as f:
    lines = f.readlines()

# Find the line with the buggy condition and fix it
fixed_count = 0
for i, line in enumerate(lines):
    if "!pasteIntoField && clipboardPath.endsWith('.id')" in line:
        # Replace this line with the fixed version
        lines[i] = line.replace(
            "!pasteIntoField && clipboardPath.endsWith('.id')",
            "!pasteIntoField && clipboardPath === `${pathToReplace}.id`"
        )
        fixed_count += 1
        print(f"Fixed line {i+1}")

with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"Applied {fixed_count} fix(es)")
PYEOF

# Verify the fix was applied
grep -n "clipboardPath ===" packages/ui/src/elements/ClipboardAction/mergeFormStateFromClipboard.ts