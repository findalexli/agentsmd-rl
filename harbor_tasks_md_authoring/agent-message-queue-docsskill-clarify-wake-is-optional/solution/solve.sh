#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-message-queue

# Idempotency guard
if grep -qF "> **AI agents**: Skip this section. Wake requires an interactive terminal with T" ".claude/skills/amq-cli/SKILL.md" && grep -qF "> **AI agents**: Skip this section. Wake requires an interactive terminal with T" ".codex/skills/amq-cli/SKILL.md" && grep -qF "> **AI agents**: Skip this section. Wake requires an interactive terminal with T" "skills/amq-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/amq-cli/SKILL.md b/.claude/skills/amq-cli/SKILL.md
@@ -21,9 +21,9 @@ Verify: `amq --version`
 ## Quick Reference
 
 ```bash
-# One-liner setup (run once per terminal session)
-eval "$(amq env --me claude --wake)"   # For Claude Code
-eval "$(amq env --me codex --wake)"    # For Codex CLI
+# Required setup (run once per terminal session)
+eval "$(amq env --me claude)"    # For Claude Code
+eval "$(amq env --me codex)"     # For Codex CLI
 
 # Send and receive messages
 amq send --to codex --body "Message"           # Send
@@ -80,9 +80,11 @@ amq init --root .agent-mail/auth --agents claude,codex
 amq init --root .agent-mail/api --agents claude,codex
 ```
 
-### Wake Notifications (Experimental)
+### Wake Notifications (Optional, Interactive Terminals Only)
 
-Start a background waker before your CLI to receive notifications when messages arrive:
+> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `amq watch` to check for messages.
+
+For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:
 
 ```bash
 amq wake &
@@ -183,10 +185,10 @@ export AMQ_NO_UPDATE_CHECK=1   # Disable update hints globally
 ### Environment Setup
 ```bash
 amq env                      # Output shell exports (auto-detects .amqrc or .agent-mail/)
-amq env --wake               # Include 'amq wake &' in output
 amq env --me codex           # Override agent handle
 amq env --shell fish         # Fish shell syntax
 amq env --json               # Machine-readable output
+amq env --wake               # Include 'amq wake &' (interactive terminals only)
 ```
 
 ### Other
diff --git a/.codex/skills/amq-cli/SKILL.md b/.codex/skills/amq-cli/SKILL.md
@@ -21,9 +21,9 @@ Verify: `amq --version`
 ## Quick Reference
 
 ```bash
-# One-liner setup (run once per terminal session)
-eval "$(amq env --me claude --wake)"   # For Claude Code
-eval "$(amq env --me codex --wake)"    # For Codex CLI
+# Required setup (run once per terminal session)
+eval "$(amq env --me claude)"    # For Claude Code
+eval "$(amq env --me codex)"     # For Codex CLI
 
 # Send and receive messages
 amq send --to codex --body "Message"           # Send
@@ -80,9 +80,11 @@ amq init --root .agent-mail/auth --agents claude,codex
 amq init --root .agent-mail/api --agents claude,codex
 ```
 
-### Wake Notifications (Experimental)
+### Wake Notifications (Optional, Interactive Terminals Only)
 
-Start a background waker before your CLI to receive notifications when messages arrive:
+> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `amq watch` to check for messages.
+
+For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:
 
 ```bash
 amq wake &
@@ -183,10 +185,10 @@ export AMQ_NO_UPDATE_CHECK=1   # Disable update hints globally
 ### Environment Setup
 ```bash
 amq env                      # Output shell exports (auto-detects .amqrc or .agent-mail/)
-amq env --wake               # Include 'amq wake &' in output
 amq env --me codex           # Override agent handle
 amq env --shell fish         # Fish shell syntax
 amq env --json               # Machine-readable output
+amq env --wake               # Include 'amq wake &' (interactive terminals only)
 ```
 
 ### Other
diff --git a/skills/amq-cli/SKILL.md b/skills/amq-cli/SKILL.md
@@ -21,9 +21,9 @@ Verify: `amq --version`
 ## Quick Reference
 
 ```bash
-# One-liner setup (run once per terminal session)
-eval "$(amq env --me claude --wake)"   # For Claude Code
-eval "$(amq env --me codex --wake)"    # For Codex CLI
+# Required setup (run once per terminal session)
+eval "$(amq env --me claude)"    # For Claude Code
+eval "$(amq env --me codex)"     # For Codex CLI
 
 # Send and receive messages
 amq send --to codex --body "Message"           # Send
@@ -80,9 +80,11 @@ amq init --root .agent-mail/auth --agents claude,codex
 amq init --root .agent-mail/api --agents claude,codex
 ```
 
-### Wake Notifications (Experimental)
+### Wake Notifications (Optional, Interactive Terminals Only)
 
-Start a background waker before your CLI to receive notifications when messages arrive:
+> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `amq watch` to check for messages.
+
+For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:
 
 ```bash
 amq wake &
@@ -183,10 +185,10 @@ export AMQ_NO_UPDATE_CHECK=1   # Disable update hints globally
 ### Environment Setup
 ```bash
 amq env                      # Output shell exports (auto-detects .amqrc or .agent-mail/)
-amq env --wake               # Include 'amq wake &' in output
 amq env --me codex           # Override agent handle
 amq env --shell fish         # Fish shell syntax
 amq env --json               # Machine-readable output
+amq env --wake               # Include 'amq wake &' (interactive terminals only)
 ```
 
 ### Other
PATCH

echo "Gold patch applied."
