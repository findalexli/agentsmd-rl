#!/usr/bin/env bash
set -euo pipefail

cd /workspace/loop

# Idempotency guard
if grep -qF "- Running `loop` with no args starts the paired interactive tmux workspace (`--t" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,15 +6,18 @@ Please keep the code dead-simple and keep the `src/loop/main.ts` file under 150
 - Check lint/types/style: `bun run check`
 - Run tests: `bun test`
 - Build executable: `bun run build`
+- Install global binary/aliases: `bun run install:global`
+- Cut a patch release: `bun run release:patch`
 
 # Repo Workflows
 
 - Plain-text prompts auto-create `PLAN.md` first, then optionally run `--review-plan`; if you are changing planning behavior, keep that flow aligned.
 - Default CLI behavior is paired Claude/Codex execution with persisted run state under `~/.loop/runs`; preserve `--run-id` / `--session` resume behavior when changing startup, planning, or loop flow.
-- Running `loop` with no args opens the live panel for active sessions, loop-owned paired runs, and tmux sessions; keep panel-only changes separate from task-running changes when possible.
+- Running `loop` with no args starts the paired interactive tmux workspace (`--tmux`); `loop dashboard` opens the live panel for active sessions, loop-owned paired runs, and tmux sessions. Keep panel-only changes separate from task-running changes when possible.
 - `--tmux` and `--worktree` are first-class execution modes. In paired mode, tmux opens Claude/Codex side-by-side and resumed run ids should stay aligned with matching tmux/worktree names.
 - `--claude-only` and `--codex-only` switch out of the default paired flow; keep single-agent behavior working when changing shared CLI parsing or resume logic.
 - `loop update` / `loop upgrade` are supported manual update commands for installed binaries; source runs should continue to rely on `git pull`.
+- When options are provided without a prompt, `loop` reuses `PLAN.md` if it already exists; keep that fallback aligned with the plain-text prompt planning flow.
 
 # Coding Standards
 
PATCH

echo "Gold patch applied."
