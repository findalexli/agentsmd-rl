#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: skip if already applied.
if grep -q "^## GitHub$" AGENTS.md 2>/dev/null; then
    echo "Solution already applied."
    exit 0
fi

# Step 1: reformat the existing branch-prefixes line to match the rest of
# the file's bullet/bold style.
python3 - <<'PY'
from pathlib import Path

p = Path("AGENTS.md")
text = p.read_text()

old_line = "Branch prefixes: `feat/`, `fix/`, `chore/`\n"
new_line = "- **Branch prefixes**: use the following prefixes for branches: `feat/`, `fix/`, `chore/`\n"
assert old_line in text, f"Expected to find {old_line!r} in AGENTS.md"
text = text.replace(old_line, new_line)
p.write_text(text)
PY

# Step 2: append the new ## GitHub section.
cat >> AGENTS.md <<'EOF'

## GitHub

- **Draft PRs**: always create PRs as drafts (`gh pr create --draft`) to avoid triggering CI unnecessarily.
- **Pull requests**: do not include a "test plan" section in PR descriptions unless you actually ran tests to verify the changes or the user explicitly asked for one.
EOF

echo "Solution applied."
