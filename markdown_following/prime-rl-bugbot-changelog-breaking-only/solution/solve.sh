#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: if breaking-only language already landed, do nothing.
if grep -q 'introduces \*\*breaking\*\* configuration changes' .cursor/BUGBOT.md 2>/dev/null; then
    echo "Gold already applied; nothing to do."
    exit 0
fi

cat > .cursor/BUGBOT.md <<'BUGBOT_EOF'
# BugBot Instructions

## Changelog Enforcement

Any PR that introduces **breaking** configuration changes must update `CHANGELOG.md`. Breaking changes are those that require users to update existing configs:

- **Renamed** config fields (old name no longer accepted)
- **Removed** config fields (field deleted or moved to a different path)
- **Moved** config fields (field relocated in the config hierarchy)

Additive changes (new fields with defaults, new optional features) and default value changes do **not** require a changelog entry.

Config files live in:

- `src/prime_rl/configs/`

If breaking changes are detected without a corresponding `CHANGELOG.md` update, request that the author add an entry.
BUGBOT_EOF

# Replace ONLY the second line (description) of CHANGELOG.md, leaving the
# entries below untouched.
python3 - <<'PY_EOF'
from pathlib import Path
p = Path("CHANGELOG.md")
lines = p.read_text().splitlines(keepends=True)
# Line 0: "# Changelog\n"; line 1: blank; line 2: old description.
new_desc = "Documenting **breaking** configuration changes — renamed, removed, or moved fields that require users to update existing configs.\n"
assert lines[0].startswith("# Changelog"), f"unexpected line 0: {lines[0]!r}"
assert lines[2].startswith("Documenting changes which affect configuration"), f"unexpected line 2: {lines[2]!r}"
lines[2] = new_desc
p.write_text("".join(lines))
PY_EOF

echo "Gold applied."
