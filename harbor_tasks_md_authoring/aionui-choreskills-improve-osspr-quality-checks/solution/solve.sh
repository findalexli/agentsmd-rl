#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aionui

# Idempotency guard
if grep -qF "1. bun run format (ALWAYS) && bun run lint && bunx tsc --noEmit (skip lint/tsc i" ".claude/skills/oss-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/oss-pr/SKILL.md b/.claude/skills/oss-pr/SKILL.md
@@ -49,14 +49,16 @@ Create branch `{username}/{type}/{slug}` directly and announce the name chosen.
 
 ### Step 1: Quality Checks
 
-```bash
-bun run lint
-bun run format
-bunx tsc --noEmit
-```
+| Command             | Scope                     | Skip when                   |
+| ------------------- | ------------------------- | --------------------------- |
+| `bun run format`    | `.ts/.tsx/.css/.json/.md` | **Never** — always run      |
+| `bun run lint`      | `.ts/.tsx` only           | No `.ts/.tsx` files changed |
+| `bunx tsc --noEmit` | `.ts/.tsx` only           | No `.ts/.tsx` files changed |
+
+Run in this order: `format` → `lint` → `tsc`.
 
+- **format** → Auto-fixes silently (must run even for non-code files like `.md`).
 - **lint fails** → Stop, report errors. Do not proceed.
-- **format** → Auto-fixes silently.
 - **tsc fails** → Stop, report errors. Do not proceed.
 - **All pass** → Proceed to i18n check below.
 
@@ -135,7 +137,7 @@ Output the PR URL when done.
 
 ```
 0. Check branch (create if on main)
-1. bun run lint && bun run format && bunx tsc --noEmit
+1. bun run format (ALWAYS) && bun run lint && bunx tsc --noEmit (skip lint/tsc if no .ts/.tsx)
    (if i18n files changed: bun run i18n:types && node scripts/check-i18n.js)
 2. bunx vitest run
 3. Commit (conventional commits, no AI attribution)
PATCH

echo "Gold patch applied."
