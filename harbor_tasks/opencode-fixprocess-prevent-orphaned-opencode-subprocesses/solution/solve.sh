#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q "THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE" AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fix AGENTS.md
python3 << PYEOF
import re

with open("/workspace/opencode/AGENTS.md", "r") as f:
    content = f.read()

old_text = "Prefer single word names for variables and functions. Only use multiple words if necessary."
new_text = """Prefer single word names for variables and functions. Only use multiple words if necessary.

### Naming Enforcement (Read This)

THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE.

- Use single word names by default for new locals, params, and helper functions.
- Multi-word names are allowed only when a single word would be unclear or ambiguous.
- Do not introduce new camelCase compounds when a short single-word alternative is clear.
- Before finishing edits, review touched lines and shorten newly introduced identifiers where possible.
- Good short names to prefer: \`pid\`, \`cfg\`, \`err\`, \`opts\`, \`dir\`, \`root\`, \`child\`, \`state\`, \`timeout\`.
- Examples to avoid unless truly required: \`inputPID\`, \`existingClient\`, \`connectTimeout\`, \`workerPath\`."""

if old_text in content:
    content = content.replace(old_text, new_text)
    with open("/workspace/opencode/AGENTS.md", "w") as f:
        f.write(content)
    print("AGENTS.md updated successfully")
else:
    print("WARNING: Could not find insertion point in AGENTS.md")
    exit(1)
PYEOF

# Fix worker.ts
python3 << PYEOF
with open("/workspace/opencode/packages/opencode/src/cli/cmd/tui/worker.ts", "r") as f:
    content = f.read()

old_block = """await Promise.race([
      Instance.disposeAll(),
      new Promise((resolve) => {
        setTimeout(resolve, 5000)
      }),
    ])"""

if old_block in content:
    content = content.replace(old_block, "await Instance.disposeAll()")
    with open("/workspace/opencode/packages/opencode/src/cli/cmd/tui/worker.ts", "w") as f:
        f.write(content)
    print("worker.ts updated successfully")
else:
    print("ERROR: Could not find Promise.race block in worker.ts")
    exit(1)
PYEOF

echo "All patches applied successfully."
