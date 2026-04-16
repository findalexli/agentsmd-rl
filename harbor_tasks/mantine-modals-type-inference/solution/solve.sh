#!/bin/bash
set -e

cd /workspace/mantine

FILE="packages/@mantine/modals/src/context.ts"

# Check if already applied (idempotency)
if grep -q "export type MantineModals = MantineModalsOverride extends { modals: infer M }" "$FILE"; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Replace the old type definition with the new one using sed
# First, remove the MantineModalsOverwritten type and MantineModals line (lines 44-53 approximately)
# Then insert the new type definition

# Create a backup
cp "$FILE" "$FILE.bak"

# Use Python for reliable multi-line replacement
python3 << 'EOF'
import re

file_path = "packages/@mantine/modals/src/context.ts"

with open(file_path, 'r') as f:
    content = f.read()

# Pattern to match the old type definition
old_pattern = r'''export type MantineModalsOverwritten = MantineModalsOverride extends \{
  modals: Record<string, React\.FC<ContextModalProps<any>>>;
\}
  \? MantineModalsOverride
  : \{
      modals: Record<string, React\.FC<ContextModalProps<any>>>;
    \};

export type MantineModals = MantineModalsOverwritten\['modals'\];'''

# New replacement
new_type = '''export type MantineModals = MantineModalsOverride extends { modals: infer M }
  ? M
  : Record<string, React.FC<ContextModalProps<any>>>;'''

# Replace
new_content = re.sub(old_pattern, new_type, content)

if new_content == content:
    print("ERROR: Pattern not found, replacement failed")
    exit(1)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Replacement successful")
EOF

rm "$FILE.bak"

echo "Patch applied successfully"
