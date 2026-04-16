#!/bin/bash
set -e

cd /workspace/effect

# Apply the fix: add { stream: true } to TextDecoder.decode() call
# This enables buffering of incomplete multi-byte UTF-8 sequences
# across chunk boundaries in Stream.decodeText
python3 -c "
import re
with open('packages/effect/src/internal/stream.ts', 'r') as f:
    content = f.read()
# Replace the specific line
old = 'return map(self, (s) => decoder.decode(s))'
new = 'return map(self, (s) => decoder.decode(s, { stream: true }))'
if old not in content:
    raise Exception(f'Could not find: {old}')
content = content.replace(old, new)
with open('packages/effect/src/internal/stream.ts', 'w') as f:
    f.write(content)
print('Patch applied successfully')
"

# Verify patch applied
grep -q "decoder.decode(s, { stream: true })" packages/effect/src/internal/stream.ts