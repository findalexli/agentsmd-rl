#!/bin/bash
set -e

cd /workspace/superset

TARGET_FILE="superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx"

# Use Python to perform the modifications
python3 << 'PYTHON_SCRIPT'
import re

# Read the file
with open('superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx', 'r') as f:
    content = f.read()

# Add the new function after sortHierarchicalObject function
# Find the pattern: the closing brace of sortHierarchicalObject followed by function convertToArray
old_pattern = r'(function sortHierarchicalObject[\s\S]*?^}\s*\n)(function convertToArray)'
new_replacement = r'''\1
function convertToNumberIfNumeric(value: string): string | number {
  const n = Number(value);
  return value.trim() !== '' && !Number.isNaN(n) ? n : value;
}

\2'''

content = re.sub(old_pattern, new_replacement, content, flags=re.MULTILINE)

# Update the column header formatter call
old_col = 'dateFormatters?.[attrName]?.(colKey[attrIdx]) ?? colKey[attrIdx]'
new_col = 'dateFormatters?.[attrName]?.(convertToNumberIfNumeric(colKey[attrIdx])) ?? colKey[attrIdx]'
content = content.replace(old_col, new_col)

# Update the row header formatter call
old_row = 'dateFormatters?.[rowAttrs[i]]?.(r) ?? r'
new_row = 'dateFormatters?.[rowAttrs[i]]?.(convertToNumberIfNumeric(r)) ?? r'
content = content.replace(old_row, new_row)

# Write back
with open('superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx', 'w') as f:
    f.write(content)

print("Changes applied successfully")
PYTHON_SCRIPT

echo "Patch applied successfully"
