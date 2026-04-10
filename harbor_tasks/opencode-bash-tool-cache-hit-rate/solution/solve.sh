#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if already fixed
if ! grep -q '\${directory}' packages/opencode/src/tool/bash.txt 2>/dev/null; then
    echo "Already applied."
    exit 0
fi

# Fix bash.txt: replace ${directory} with static text
sed -i 's/\${directory}/current working directory/' packages/opencode/src/tool/bash.txt

# Fix bash.ts: remove the .replaceAll("${directory}", Instance.directory) call
# Original:
#   description: DESCRIPTION.replaceAll("${directory}", Instance.directory)
#     .replaceAll("${maxLines}", String(Truncate.MAX_LINES))
#     .replaceAll("${maxBytes}", String(Truncate.MAX_BYTES)),
# Fixed:
#   description: DESCRIPTION.replaceAll("${maxLines}", String(Truncate.MAX_LINES)).replaceAll(
#     "${maxBytes}",
#     String(Truncate.MAX_BYTES),
#   ),

cd packages/opencode/src/tool

python3 -c "
import re

with open('bash.ts', 'r') as f:
    content = f.read()

# Replace the multi-line description construction
old = '''description: DESCRIPTION.replaceAll(\"\${directory}\", Instance.directory)
      .replaceAll(\"\${maxLines}\", String(Truncate.MAX_LINES))
      .replaceAll(\"\${maxBytes}\", String(Truncate.MAX_BYTES)),'''

new = '''description: DESCRIPTION.replaceAll(\"\${maxLines}\", String(Truncate.MAX_LINES)).replaceAll(
      \"\${maxBytes}\",
      String(Truncate.MAX_BYTES),
    ),'''

content = content.replace(old, new)

with open('bash.ts', 'w') as f:
    f.write(content)
"

echo "Patch applied successfully."

cd /workspace/opencode
echo "" >> AGENTS.md
echo "Do not inject project-specific paths like \${directory} into tool descriptions, as this breaks LLM prompt caching. Use static text (e.g., 'current working directory') instead." >> AGENTS.md
