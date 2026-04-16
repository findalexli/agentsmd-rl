#!/bin/bash
set -e

cd /workspace/antd

TARGET_FILE="components/date-picker/style/panel.ts"

# Check if patch already applied (idempotency)
if grep -q "overflowY: 'auto'," "$TARGET_FILE" 2>/dev/null; then
    # Check if we also removed the hover rule
    if ! grep -A1 "'&:hover':" "$TARGET_FILE" | grep -q "overflowY: 'auto'"; then
        echo "Patch already applied, skipping..."
        exit 0
    fi
fi

# Step 1: Change overflowY: 'hidden' to overflowY: 'auto' in the time-panel-column
# This is the first occurrence in the &-column block (around line 542)
sed -i "s/overflowY: 'hidden',/overflowY: 'auto',/" "$TARGET_FILE"

# Step 2: Remove the '&:hover': { overflowY: 'auto', } block (lines 578-580)
# This removes the now-unnecessary hover override
sed -i "/'&:hover': {/{
N
/overflowY: 'auto',/{
N
s/'&:hover': {\n *overflowY: 'auto',\n *},//
}
}" "$TARGET_FILE"

echo "Patch applied successfully"
