#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if already fixed
if ! grep -q '${directory}' packages/opencode/src/tool/bash.txt 2>/dev/null; then
    echo 'Already applied.'
    exit 0
fi

# Fix bash.txt: replace ${directory} with static text
sed -i 's/\${directory}/current working directory/' packages/opencode/src/tool/bash.txt

# Create a Python script to fix bash.ts
cat > /tmp/fix_bash_ts.py << 'EOF'
import re

with open('packages/opencode/src/tool/bash.ts', 'r') as f:
    content = f.read()

# Replace the multi-line pattern
old_pattern = '''description: DESCRIPTION.replaceAll("${directory}", Instance.directory)
      .replaceAll("${maxLines}", String(Truncate.MAX_LINES))
      .replaceAll("${maxBytes}", String(Truncate.MAX_BYTES)),'''

new_pattern = '''description: DESCRIPTION.replaceAll("${maxLines}", String(Truncate.MAX_LINES)).replaceAll(
      "${maxBytes}",
      String(Truncate.MAX_BYTES),
    ),'''

content = content.replace(old_pattern, new_pattern)

with open('packages/opencode/src/tool/bash.ts', 'w') as f:
    f.write(content)

print('Fixed bash.ts')
EOF

python3 /tmp/fix_bash_ts.py

# Run prettier to fix formatting
cd /workspace/opencode/packages/opencode
npx prettier --write src/tool/bash.ts --parser typescript || true

cd /workspace/opencode
echo 'Patch applied successfully.'

# Stage and commit the code changes
git add packages/opencode/src/tool/bash.txt packages/opencode/src/tool/bash.ts
git commit -m 'Fix: Remove ${directory} placeholder from BashTool description'

# Add AGENTS.md documentation (inlining note first, then directory note)
echo '' >> AGENTS.md
echo 'When defining tool descriptions, inline the description construction by chaining `.replaceAll()` calls directly on the `DESCRIPTION` constant rather than extracting intermediate values.' >> AGENTS.md
echo '' >> AGENTS.md
echo 'Do not inject project-specific paths like ${directory} into tool descriptions, as this breaks LLM prompt caching. Use static text (e.g., current working directory) instead.' >> AGENTS.md
git add AGENTS.md
git commit -m 'Docs: Add AGENTS.md notes about tool descriptions'
