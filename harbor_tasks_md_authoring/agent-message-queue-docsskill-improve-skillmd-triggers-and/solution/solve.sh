#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-message-queue

# Idempotency guard
if grep -qF "description: Coordinate agents via the AMQ CLI for file-based inter-agent messag" ".claude/skills/amq-cli/SKILL.md" && grep -qF "description: Coordinate agents via the AMQ CLI for file-based inter-agent messag" ".codex/skills/amq-cli/SKILL.md" && grep -qF "description: Coordinate agents via the AMQ CLI for file-based inter-agent messag" "skills/amq-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/amq-cli/SKILL.md b/.claude/skills/amq-cli/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: amq-cli
-description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co-op mode between Claude Code and Codex CLI, or manage agent-to-agent communication in any multi-agent workflow.
+description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co-op mode between Claude Code and Codex CLI, or manage agent-to-agent communication in any multi-agent workflow. Triggers include "message codex", "talk to claude", "collaborate with partner agent", "AMQ", "inter-agent messaging", or "agent coordination".
 metadata:
   short-description: Inter-agent messaging via AMQ CLI
 ---
@@ -78,11 +78,6 @@ AMQ: message from codex - Review complete. Run: amq drain --include-body
 
 Then run `amq drain --include-body` to read messages.
 
-## References
-
-- `references/coop-mode.md` — co-op coordination protocol
-- `references/message-format.md` — frontmatter schema cheatsheet
-
 **Inject Modes**: The wake command auto-detects your CLI type:
 - `--inject-mode=auto` (default): Uses `raw` for Claude Code/Codex, `paste` for others
 - `--inject-mode=raw`: Plain text + CR (best for Ink-based CLIs like Claude Code)
@@ -181,4 +176,9 @@ amq send --to codex --kind review_request \
 - Delivery: atomic Maildir (tmp -> new -> cur)
 - Never edit message files directly
 
-See [COOP.md](https://github.com/avivsinai/agent-message-queue/blob/main/COOP.md) for full protocol.
+## References
+
+Read these when you need deeper context:
+
+- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents
+- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)
diff --git a/.codex/skills/amq-cli/SKILL.md b/.codex/skills/amq-cli/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: amq-cli
-description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co-op mode between Claude Code and Codex CLI, or manage agent-to-agent communication in any multi-agent workflow.
+description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co-op mode between Claude Code and Codex CLI, or manage agent-to-agent communication in any multi-agent workflow. Triggers include "message codex", "talk to claude", "collaborate with partner agent", "AMQ", "inter-agent messaging", or "agent coordination".
 metadata:
   short-description: Inter-agent messaging via AMQ CLI
 ---
@@ -78,11 +78,6 @@ AMQ: message from codex - Review complete. Run: amq drain --include-body
 
 Then run `amq drain --include-body` to read messages.
 
-## References
-
-- `references/coop-mode.md` — co-op coordination protocol
-- `references/message-format.md` — frontmatter schema cheatsheet
-
 **Inject Modes**: The wake command auto-detects your CLI type:
 - `--inject-mode=auto` (default): Uses `raw` for Claude Code/Codex, `paste` for others
 - `--inject-mode=raw`: Plain text + CR (best for Ink-based CLIs like Claude Code)
@@ -181,4 +176,9 @@ amq send --to codex --kind review_request \
 - Delivery: atomic Maildir (tmp -> new -> cur)
 - Never edit message files directly
 
-See [COOP.md](https://github.com/avivsinai/agent-message-queue/blob/main/COOP.md) for full protocol.
+## References
+
+Read these when you need deeper context:
+
+- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents
+- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)
diff --git a/skills/amq-cli/SKILL.md b/skills/amq-cli/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: amq-cli
-description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co-op mode between Claude Code and Codex CLI, or manage agent-to-agent communication in any multi-agent workflow.
+description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co-op mode between Claude Code and Codex CLI, or manage agent-to-agent communication in any multi-agent workflow. Triggers include "message codex", "talk to claude", "collaborate with partner agent", "AMQ", "inter-agent messaging", or "agent coordination".
 metadata:
   short-description: Inter-agent messaging via AMQ CLI
 ---
@@ -78,11 +78,6 @@ AMQ: message from codex - Review complete. Run: amq drain --include-body
 
 Then run `amq drain --include-body` to read messages.
 
-## References
-
-- `references/coop-mode.md` — co-op coordination protocol
-- `references/message-format.md` — frontmatter schema cheatsheet
-
 **Inject Modes**: The wake command auto-detects your CLI type:
 - `--inject-mode=auto` (default): Uses `raw` for Claude Code/Codex, `paste` for others
 - `--inject-mode=raw`: Plain text + CR (best for Ink-based CLIs like Claude Code)
@@ -181,4 +176,9 @@ amq send --to codex --kind review_request \
 - Delivery: atomic Maildir (tmp -> new -> cur)
 - Never edit message files directly
 
-See [COOP.md](https://github.com/avivsinai/agent-message-queue/blob/main/COOP.md) for full protocol.
+## References
+
+Read these when you need deeper context:
+
+- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents
+- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)
PATCH

echo "Gold patch applied."
