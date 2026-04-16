#!/bin/bash
set -e

cd /workspace/redux-toolkit

# Check if already patched (idempotency)
if grep -q "meta: pageResponse.meta," packages/toolkit/src/query/core/buildThunks.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply fixes using Python for reliable multi-line edits
python3 << 'PYTHON'
import re

# Fix 1: Add meta handling in buildThunks.ts
with open('packages/toolkit/src/query/core/buildThunks.ts', 'r') as f:
    content = f.read()

# Find the pattern where we need to add meta - after the closing brace of data object
# Look for the pattern where we return the object with data property for infinite queries
old_pattern = r'''(
          data: \{
            pages: addTo\(data\.pages, pageResponse\.data, maxPages\),
            pageParams: addTo\(data\.pageParams, param, maxPages\),
          \},
        \})'''

new_replacement = r'''\1,
          meta: pageResponse.meta,'''

# Actually, let's use a simpler approach - find the specific context
# Find: pageParams: addTo(data.pageParams, param, maxPages),
#       },
# And add meta after the closing brace

lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    # Check if this is the line with pageParams in the infinite query result handling
    if 'pageParams: addTo(data.pageParams, param, maxPages),' in line and i + 1 < len(lines):
        next_line = lines[i + 1]
        # Check if next line closes the data object (should be '          },')
        if next_line.strip() == '},':
            new_lines.append(next_line)  # Add the closing brace
            # Add the meta line with proper indentation (10 spaces to match data:)
            new_lines.append('          meta: pageResponse.meta,')
            i += 2
            continue
    i += 1

content = '\n'.join(new_lines)

with open('packages/toolkit/src/query/core/buildThunks.ts', 'w') as f:
    f.write(content)

print("Updated buildThunks.ts")

# Fix 2: Update infiniteQueries.test.ts - replace meta: undefined with meta containing request/response
with open('packages/toolkit/src/query/tests/infiniteQueries.test.ts', 'r') as f:
    content = f.read()

old_meta = "meta: undefined,"
new_meta = """meta: expect.objectContaining({
        request: expect.anything(),
        response: expect.anything(),
      }),"""

count = content.count(old_meta)
print(f"Found {count} occurrences of '{old_meta}'")

content = content.replace(old_meta, new_meta)

with open('packages/toolkit/src/query/tests/infiniteQueries.test.ts', 'w') as f:
    f.write(content)

print("Updated infiniteQueries.test.ts")
PYTHON

echo "Patch applied successfully"
