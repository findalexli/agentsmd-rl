#!/bin/bash
set -e

cd /workspace/selenium

TARGET_FILE="java/src/org/openqa/selenium/json/InstanceCoercer.java"

# Idempotency check - if fix is already applied, exit successfully
if grep -q "Duplicate JSON field name detected while collecting field writers" "$TARGET_FILE" 2>/dev/null; then
    echo "Fix already applied, skipping patch"
    exit 0
fi

# Use sed to add the merge function to Collectors.toMap in getFieldWriters method
# The fix adds a third argument to handle duplicate keys
# Only modify line 129 (the })); after the first return new TypeAndWriter)
# Line 128 has: return new TypeAndWriter(type, writer);
# Line 129 has: }));

sed -i '129s/}));$/},\n                (existing, replacement) -> {\n                  throw new JsonException(\n                      "Duplicate JSON field name detected while collecting field writers");\n                }));/' "$TARGET_FILE"

# Verify the fix was applied
if grep -q "Duplicate JSON field name detected while collecting field writers" "$TARGET_FILE"; then
    echo "Patch applied successfully"
else
    echo "Failed to apply patch"
    exit 1
fi
