#!/usr/bin/env bash
set -euo pipefail

cd /workspace/higress

# Idempotency guard
if grep -qF "3. **OpenClaw Integration**: The `openclaw models auth login` and `openclaw gate" ".claude/skills/higress-openclaw-integration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/higress-openclaw-integration/SKILL.md b/.claude/skills/higress-openclaw-integration/SKILL.md
@@ -82,20 +82,29 @@ PLUGIN_DEST="$HOME/.openclaw/extensions/higress"
 
 mkdir -p "$PLUGIN_DEST"
 cp -r "$PLUGIN_SRC"/* "$PLUGIN_DEST/"
+```
+
+**⚠️ Tell user to run the following commands manually in their terminal (interactive commands, cannot be executed by AI agent):**
 
-# Configure provider
+```bash
+# Step 1: Enable the plugin
 openclaw plugins enable higress
+
+# Step 2: Configure provider (interactive - will prompt for Gateway URL, API Key, models, etc.)
 openclaw models auth login --provider higress --set-default
+
+# Step 3: Restart OpenClaw gateway to apply changes
+openclaw gateway restart
 ```
 
-The `openclaw models auth login` command will prompt for:
+The `openclaw models auth login` command will interactively prompt for:
 1. Gateway URL (default: `http://localhost:8080`)
 2. Console URL (default: `http://localhost:8001`)
 3. API Key (optional for local deployments)
 4. Model list (auto-detected or manually specified)
 5. Auto-routing default model (if using `higress/auto`)
 
-After configuration, Higress models are available in OpenClaw with `higress/` prefix (e.g., `higress/glm-4`, `higress/auto`).
+After configuration and restart, Higress models are available in OpenClaw with `higress/` prefix (e.g., `higress/glm-4`, `higress/auto`).
 
 ## Post-Deployment Management
 
@@ -168,5 +177,5 @@ curl 'http://localhost:8080/v1/chat/completions' \
 
 1. **Claude Code Mode**: Requires OAuth token from `claude setup-token` command, not a regular API key
 2. **Auto-routing**: Must be enabled during initial deployment (`--auto-routing`); routing rules can be added later
-3. **OpenClaw Integration**: After plugin installation and `openclaw models auth login --provider higress`, models are available with `higress/` prefix
+3. **OpenClaw Integration**: The `openclaw models auth login` and `openclaw gateway restart` commands are **interactive** and must be run by the user manually in their terminal
 4. **Hot-reload**: API key changes take effect immediately; no container restart needed
PATCH

echo "Gold patch applied."
