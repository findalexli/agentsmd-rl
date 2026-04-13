#!/bin/bash
# Fix: Update CLAUDE.md indentation from 4 spaces to 2 spaces

set -e

# Copy repo to writable location
mkdir -p /tmp/writable-repo
cp -r "$REPO"/* /tmp/writable-repo/

# Use Python to convert indentation:
# Any line with leading spaces gets exactly 2-space indentation
# This converts 4-space, 8-space, etc. all to flat 2-space
python3 << 'PYTHON_SCRIPT'
content = open('/tmp/writable-repo/CLAUDE.md').read()
lines = content.split('\n')
result = []
for line in lines:
    # If line has any 4-space (or more) indentation, convert to flat 2-space
    if line.startswith('    '):
        # Strip all leading 4-space groups and add a single 2-space indent
        while line.startswith('    '):
            line = line[4:]
        result.append('  ' + line)
    else:
        result.append(line)
open('/tmp/writable-repo/CLAUDE.md', 'w').write('\n'.join(result))
PYTHON_SCRIPT

# Copy the fixed file back - write directly to handle read-only mount
cat /tmp/writable-repo/CLAUDE.md > "$REPO/CLAUDE.md"
