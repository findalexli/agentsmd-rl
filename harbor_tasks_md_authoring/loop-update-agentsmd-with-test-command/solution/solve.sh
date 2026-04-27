#!/usr/bin/env bash
set -euo pipefail

cd /workspace/loop

# Idempotency guard
if grep -qF "- Plain-text prompts auto-create `PLAN.md` first, then optionally run `--review-" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -4,8 +4,16 @@ Please keep the code dead-simple and keep the `src/loop/main.ts` file under 150
 
 - Format code: `bun run fix`
 - Check lint/types/style: `bun run check`
+- Run tests: `bun test`
 - Build executable: `bun run build`
 
+# Repo Workflows
+
+- Plain-text prompts auto-create `PLAN.md` first, then optionally run `--review-plan`; if you are changing planning behavior, keep that flow aligned.
+- Running `loop` with no args opens the live panel for active sessions; keep panel-only changes separate from task-running changes when possible.
+- `--tmux` and `--worktree` are first-class execution modes; preserve them when changing CLI parsing or startup flow.
+- `loop update` / `loop upgrade` are supported manual update commands for installed binaries; source runs should continue to rely on `git pull`.
+
 # Coding Standards
 
 - Keep functions small and easy to read.
PATCH

echo "Gold patch applied."
