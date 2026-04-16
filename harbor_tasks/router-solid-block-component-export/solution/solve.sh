#!/bin/bash
set -e

cd /workspace/router

TARGET_FILE="packages/solid-router/src/useBlocker.tsx"

# Check if already patched (idempotency check)
if grep -q "export const Block: BlockComponent" "$TARGET_FILE"; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Create a temp file with the new content
temp_file=$(mktemp)

# Use awk to perform the replacement precisely
awk '
/^\/\*\*$/ {
    # Check if next line contains the deprecated message
    getline next_line
    if (next_line ~ /@deprecated.*Use the UseBlockerOpts property instead/) {
        # Skip the JSDoc comment lines until we find export function Block
        while (getline > 0) {
            if ($0 ~ /^export function Block\(opts: LegacyPromptProps\): SolidNode$/) {
                # Skip this line too (the deprecated overload)
                break
            }
        }
        next
    } else {
        # Not our target, print the /** and the line we read
        print "/**"
        print next_line
        next
    }
}

/^export function Block\(opts: PromptProps \| LegacyPromptProps\): SolidNode \{$/ {
    # Replace the implementation function signature with const declaration
    print "export const Block: BlockComponent = function Block("
    print "  opts: PromptProps | LegacyPromptProps,"
    print "): SolidNode {"
    next
}

{ print }
' "$TARGET_FILE" > "$temp_file"

# Replace the original file
mv "$temp_file" "$TARGET_FILE"

echo "Patch applied successfully"
