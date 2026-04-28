#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "The code must explicitly output results using `echo`, `dump`, or similar \u2014 expre" "laravel-cloud/skills/deploying-laravel-cloud/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/laravel-cloud/skills/deploying-laravel-cloud/SKILL.md b/laravel-cloud/skills/deploying-laravel-cloud/SKILL.md
@@ -96,6 +96,42 @@ Use your judgment:
 - Order of provisioning — no strict sequence required
 - How to present output — summarize, show raw, or extract fields based on context
 
+## Remote Access
+
+### Tinker (> v0.2.0)
+
+Run PHP code directly in a Cloud environment:
+
+```sh
+cloud tinker {environment} --code='Your PHP code here' --timeout=60 -n
+```
+
+- `--code` — PHP code to execute (required in non-interactive mode)
+- `--timeout` — max seconds to wait for output (default: 60)
+
+The code must explicitly output results using `echo`, `dump`, or similar — expressions alone produce no output.
+
+Always pass `--code` and `-n` to avoid interactive prompts.
+
+### Remote Commands
+
+Run shell commands on a Cloud environment:
+
+```sh
+cloud command:run {environment} --cmd='your command here' -n
+```
+
+- `--cmd` — the command to run (required in non-interactive mode)
+- `--no-monitor` — skip real-time output streaming
+- `--copy-output` — copy output to clipboard
+
+Review past commands:
+
+- `cloud command:list {environment} --json -n` — list command history
+- `cloud command:get {commandId} --json -n` — get details and output of a specific command
+
+Delegate `command:run` to a subagent when output may be long.
+
 ## Config
 
 1. Global: `~/.config/cloud/config.json` — auth tokens and preferences
PATCH

echo "Gold patch applied."
