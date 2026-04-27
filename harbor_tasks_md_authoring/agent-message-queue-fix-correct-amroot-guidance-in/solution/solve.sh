#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-message-queue

# Idempotency guard
if grep -qF "- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/col" ".claude/skills/amq-cli/SKILL.md" && grep -qF "- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/col" ".codex/skills/amq-cli/SKILL.md" && grep -qF "- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/col" "skills/amq-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/amq-cli/SKILL.md b/.claude/skills/amq-cli/SKILL.md
@@ -36,13 +36,25 @@ When running inside `coop exec`, the environment is already configured:
 
 When running **outside** `coop exec` (e.g. new conversation, manual terminal):
 
-- You **must** set both `AM_ME` and `AM_ROOT` explicitly on every command
-- `amq` resolves the root from `.amqrc` at call time — if `.amqrc` was changed mid-conversation, messages silently route to the new root
-- **Always use explicit `AM_ROOT`** to avoid routing to the wrong session:
+- **Use `amq env` to resolve the root** — it reads `.amqrc` and returns the base root:
   ```bash
-  AM_ME=claude AM_ROOT=/path/to/project/.agent-mail/<session> amq send --to codex --body "hello"
+  eval "$(amq env --me claude)"          # sets AM_ME + AM_ROOT from .amqrc
   ```
-- **Pitfall**: setting only `AM_ME` without `AM_ROOT` relies on `.amqrc` which may have changed. Messages will land in the wrong session's inbox with no error — the target agent won't see them.
+- Or resolve and pin explicitly per command:
+  ```bash
+  AM_ME=claude AM_ROOT=.agent-mail amq send --to codex --body "hello"
+  ```
+- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.
+- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agent-mail`. Only use a session path if the target agent is also in that session.
+
+### Root Resolution Truth-Table
+
+| Context | Command | AM_ROOT resolves to |
+|---------|---------|---------------------|
+| Outside `coop exec` | `amq env --me claude` | base root from `.amqrc` (e.g. `.agent-mail`) |
+| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |
+| Inside `coop exec` (no flags) | automatic | `.agent-mail/collab` (default session) |
+| Inside `coop exec --session X` | automatic | `.agent-mail/X` |
 
 ## Quick Start
 
diff --git a/.codex/skills/amq-cli/SKILL.md b/.codex/skills/amq-cli/SKILL.md
@@ -36,13 +36,25 @@ When running inside `coop exec`, the environment is already configured:
 
 When running **outside** `coop exec` (e.g. new conversation, manual terminal):
 
-- You **must** set both `AM_ME` and `AM_ROOT` explicitly on every command
-- `amq` resolves the root from `.amqrc` at call time — if `.amqrc` was changed mid-conversation, messages silently route to the new root
-- **Always use explicit `AM_ROOT`** to avoid routing to the wrong session:
+- **Use `amq env` to resolve the root** — it reads `.amqrc` and returns the base root:
   ```bash
-  AM_ME=claude AM_ROOT=/path/to/project/.agent-mail/<session> amq send --to codex --body "hello"
+  eval "$(amq env --me claude)"          # sets AM_ME + AM_ROOT from .amqrc
   ```
-- **Pitfall**: setting only `AM_ME` without `AM_ROOT` relies on `.amqrc` which may have changed. Messages will land in the wrong session's inbox with no error — the target agent won't see them.
+- Or resolve and pin explicitly per command:
+  ```bash
+  AM_ME=claude AM_ROOT=.agent-mail amq send --to codex --body "hello"
+  ```
+- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.
+- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agent-mail`. Only use a session path if the target agent is also in that session.
+
+### Root Resolution Truth-Table
+
+| Context | Command | AM_ROOT resolves to |
+|---------|---------|---------------------|
+| Outside `coop exec` | `amq env --me claude` | base root from `.amqrc` (e.g. `.agent-mail`) |
+| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |
+| Inside `coop exec` (no flags) | automatic | `.agent-mail/collab` (default session) |
+| Inside `coop exec --session X` | automatic | `.agent-mail/X` |
 
 ## Quick Start
 
diff --git a/skills/amq-cli/SKILL.md b/skills/amq-cli/SKILL.md
@@ -36,13 +36,25 @@ When running inside `coop exec`, the environment is already configured:
 
 When running **outside** `coop exec` (e.g. new conversation, manual terminal):
 
-- You **must** set both `AM_ME` and `AM_ROOT` explicitly on every command
-- `amq` resolves the root from `.amqrc` at call time — if `.amqrc` was changed mid-conversation, messages silently route to the new root
-- **Always use explicit `AM_ROOT`** to avoid routing to the wrong session:
+- **Use `amq env` to resolve the root** — it reads `.amqrc` and returns the base root:
   ```bash
-  AM_ME=claude AM_ROOT=/path/to/project/.agent-mail/<session> amq send --to codex --body "hello"
+  eval "$(amq env --me claude)"          # sets AM_ME + AM_ROOT from .amqrc
   ```
-- **Pitfall**: setting only `AM_ME` without `AM_ROOT` relies on `.amqrc` which may have changed. Messages will land in the wrong session's inbox with no error — the target agent won't see them.
+- Or resolve and pin explicitly per command:
+  ```bash
+  AM_ME=claude AM_ROOT=.agent-mail amq send --to codex --body "hello"
+  ```
+- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.
+- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agent-mail`. Only use a session path if the target agent is also in that session.
+
+### Root Resolution Truth-Table
+
+| Context | Command | AM_ROOT resolves to |
+|---------|---------|---------------------|
+| Outside `coop exec` | `amq env --me claude` | base root from `.amqrc` (e.g. `.agent-mail`) |
+| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |
+| Inside `coop exec` (no flags) | automatic | `.agent-mail/collab` (default session) |
+| Inside `coop exec --session X` | automatic | `.agent-mail/X` |
 
 ## Quick Start
 
PATCH

echo "Gold patch applied."
