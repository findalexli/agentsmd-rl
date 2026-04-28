#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quickadd

# Idempotency guard
if grep -qF "QuickAdd is an Obsidian community plugin that provides four choice types:" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,8 +1,16 @@
 # Repository Guidelines
 
+## Project Overview
+QuickAdd is an Obsidian community plugin that provides four choice types:
+templates, captures, macros, and multis.
+
 ## Project Structure & Module Organization
 QuickAdd is an Obsidian community plugin. Source code lives in `src/`: core logic under `engine/`, `services/`, and `utils/`; Svelte UI in `src/gui`; shared types in `src/types`; settings entry in `src/quickAddSettingsTab.ts`. Bundled artifacts `main.js` and `styles.css` stay at the repo root and should be generated, not hand-edited. Place tests and stubs in `tests/`, and keep user-facing docs in `docs/`.
 
+## Tooling & GitHub
+- Use `bun` for package management and scripts. Avoid npm/yarn/pnpm.
+- Use the GitHub CLI (`gh`) for issues, PRs, and releases.
+
 ## Build, Test, and Development Commands
 - `bun run dev`: watch-mode bundle via `esbuild.config.mjs`, regenerating `main.js` as you edit.
 - `bun run build`: run `tsc --noEmit` then produce the production bundle.
PATCH

echo "Gold patch applied."
