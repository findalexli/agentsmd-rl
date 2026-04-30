#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-message-queue

# Idempotency guard
if grep -qF ".claude/skills/amq-cli/SKILL.md" ".claude/skills/amq-cli/SKILL.md" && grep -qF ".codex/skills/amq-cli/SKILL.md" ".codex/skills/amq-cli/SKILL.md" && grep -qF "skills/amq-cli/SKILL.md" "skills/amq-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/amq-cli/SKILL.md b/.claude/skills/amq-cli/SKILL.md
@@ -72,25 +72,6 @@ By default, `.amqrc` points to a literal root (e.g., `.agent-mail`). Use `--sess
 
 Only two env vars: `AM_ROOT` (where) + `AM_ME` (who). The CLI enforces correct routing — just run `amq` commands as-is.
 
-## Environment Rules (IMPORTANT)
-
-When running inside `coop exec`, the environment is already configured. Follow these rules:
-
-- **Always use `amq` from PATH** — never `./amq`, `../amq`, or absolute paths to local binaries
-- **Never override `AM_ROOT` or `AM_ME`** — they are set by `coop exec` and point to the correct session. Do not prefix commands with `AM_ROOT=... amq ...`
-- **Never pass `--root` or `--me` flags** — the env vars handle routing automatically
-- **Just run commands as-is**: `amq send --to codex --body "hello"`
-
-Wrong:
-```bash
-AM_ROOT=.agent-mail AM_ME=claude ./amq send --to codex --body "hello"
-```
-
-Right:
-```bash
-amq send --to codex --body "hello"
-```
-
 ## Messaging
 
 ```bash
@@ -133,6 +114,7 @@ amq list --new --label bug
 | `todo` | — | normal |
 | `status` | — | low |
 | `brainstorm` | — | low |
+
 ## References
 
 For detailed protocols, read the reference file FIRST, then follow its instructions:
diff --git a/.codex/skills/amq-cli/SKILL.md b/.codex/skills/amq-cli/SKILL.md
@@ -72,25 +72,6 @@ By default, `.amqrc` points to a literal root (e.g., `.agent-mail`). Use `--sess
 
 Only two env vars: `AM_ROOT` (where) + `AM_ME` (who). The CLI enforces correct routing — just run `amq` commands as-is.
 
-## Environment Rules (IMPORTANT)
-
-When running inside `coop exec`, the environment is already configured. Follow these rules:
-
-- **Always use `amq` from PATH** — never `./amq`, `../amq`, or absolute paths to local binaries
-- **Never override `AM_ROOT` or `AM_ME`** — they are set by `coop exec` and point to the correct session. Do not prefix commands with `AM_ROOT=... amq ...`
-- **Never pass `--root` or `--me` flags** — the env vars handle routing automatically
-- **Just run commands as-is**: `amq send --to codex --body "hello"`
-
-Wrong:
-```bash
-AM_ROOT=.agent-mail AM_ME=claude ./amq send --to codex --body "hello"
-```
-
-Right:
-```bash
-amq send --to codex --body "hello"
-```
-
 ## Messaging
 
 ```bash
@@ -133,6 +114,7 @@ amq list --new --label bug
 | `todo` | — | normal |
 | `status` | — | low |
 | `brainstorm` | — | low |
+
 ## References
 
 For detailed protocols, read the reference file FIRST, then follow its instructions:
diff --git a/skills/amq-cli/SKILL.md b/skills/amq-cli/SKILL.md
@@ -72,25 +72,6 @@ By default, `.amqrc` points to a literal root (e.g., `.agent-mail`). Use `--sess
 
 Only two env vars: `AM_ROOT` (where) + `AM_ME` (who). The CLI enforces correct routing — just run `amq` commands as-is.
 
-## Environment Rules (IMPORTANT)
-
-When running inside `coop exec`, the environment is already configured. Follow these rules:
-
-- **Always use `amq` from PATH** — never `./amq`, `../amq`, or absolute paths to local binaries
-- **Never override `AM_ROOT` or `AM_ME`** — they are set by `coop exec` and point to the correct session. Do not prefix commands with `AM_ROOT=... amq ...`
-- **Never pass `--root` or `--me` flags** — the env vars handle routing automatically
-- **Just run commands as-is**: `amq send --to codex --body "hello"`
-
-Wrong:
-```bash
-AM_ROOT=.agent-mail AM_ME=claude ./amq send --to codex --body "hello"
-```
-
-Right:
-```bash
-amq send --to codex --body "hello"
-```
-
 ## Messaging
 
 ```bash
@@ -133,6 +114,7 @@ amq list --new --label bug
 | `todo` | — | normal |
 | `status` | — | low |
 | `brainstorm` | — | low |
+
 ## References
 
 For detailed protocols, read the reference file FIRST, then follow its instructions:
PATCH

echo "Gold patch applied."
