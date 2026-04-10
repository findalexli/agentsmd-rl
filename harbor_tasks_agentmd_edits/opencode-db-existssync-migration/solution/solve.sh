#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'existsSync' packages/opencode/src/storage/db.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Delete the bun-file-io SKILL.md file
rm -f .opencode/skill/bun-file-io/SKILL.md

# Update db.ts to use existsSync instead of Bun.file().size
sed -i 's/import { readFileSync, readdirSync } from "fs"/import { readFileSync, readdirSync, existsSync } from "fs"/' packages/opencode/src/storage/db.ts
sed -i 's/if (!Bun.file(file).size) return/if (!existsSync(file)) return/' packages/opencode/src/storage/db.ts

echo "Patch applied successfully."
