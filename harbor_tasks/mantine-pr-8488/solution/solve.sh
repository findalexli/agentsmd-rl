#!/bin/bash
set -e

cd /workspace/mantine

# Fetch the fixed commit
git fetch origin d26f9e6fd11cd896a4499eb4d74709a355ff8ca7 --filter=blob:none

# Generate and apply the patch
git diff ae08675 d26f9e6fd11cd896a4499eb4d74709a355ff8ca7 -- packages/@mantine/dates > /tmp/fix.patch
git apply /tmp/fix.patch

# Verify something changed
if git diff --quiet; then
    echo "ERROR: No changes were applied"
    exit 1
fi

# Verify the fix is applied (idempotency check)
if ! grep -q "controlProps?.children ??" packages/@mantine/dates/src/components/MonthsList/MonthsList.tsx; then
    echo "ERROR: Fix not applied to MonthsList.tsx"
    exit 1
fi

if ! grep -q "controlProps?.children ??" packages/@mantine/dates/src/components/YearsList/YearsList.tsx; then
    echo "ERROR: Fix not applied to YearsList.tsx"
    exit 1
fi

echo "Fix applied successfully"