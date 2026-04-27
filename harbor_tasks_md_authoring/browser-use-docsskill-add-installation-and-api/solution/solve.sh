#!/usr/bin/env bash
set -euo pipefail

cd /workspace/browser-use

# Idempotency guard
if grep -qF "Some features (`run`, `extract`, `--browser remote`) require an API key. The CLI" "skills/browser-use/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/browser-use/SKILL.md b/skills/browser-use/SKILL.md
@@ -8,6 +8,19 @@ allowed-tools: Bash(browser-use:*)
 
 The `browser-use` command provides fast, persistent browser automation. It maintains browser sessions across commands, enabling complex multi-step workflows.
 
+## Installation
+
+```bash
+# Run without installing (recommended for one-off use)
+uvx browser-use[cli] open https://example.com
+
+# Or install permanently
+uv pip install browser-use[cli]
+
+# Install browser dependencies (Chromium)
+browser-use install
+```
+
 ## Quick Start
 
 ```bash
@@ -123,6 +136,11 @@ browser-use server stop                   # Stop server
 browser-use server logs                   # View server logs
 ```
 
+### Setup
+```bash
+browser-use install                       # Install Chromium and system dependencies
+```
+
 ## Global Options
 
 | Option | Description |
@@ -136,6 +154,20 @@ browser-use server logs                   # View server logs
 
 **Session behavior**: All commands without `--session` use the same "default" session. The browser stays open and is reused across commands. Use `--session NAME` to run multiple browsers in parallel.
 
+## API Key Configuration
+
+Some features (`run`, `extract`, `--browser remote`) require an API key. The CLI checks these locations in order:
+
+1. `--api-key` command line flag
+2. `BROWSER_USE_API_KEY` environment variable
+3. `~/.config/browser-use/config.json` file
+
+To configure permanently:
+```bash
+mkdir -p ~/.config/browser-use
+echo '{"api_key": "your-key-here"}' > ~/.config/browser-use/config.json
+```
+
 ## Examples
 
 ### Form Submission
@@ -186,11 +218,13 @@ browser-use state  # Already logged in!
 4. **Use `--json` for parsing** output programmatically
 5. **Python variables persist** across `browser-use python` commands within a session
 6. **Real browser mode** preserves your login sessions and extensions
+7. **CLI aliases**: `bu`, `browser`, and `browseruse` all work identically to `browser-use`
 
 ## Troubleshooting
 
 **Browser won't start?**
 ```bash
+browser-use install                   # Install/reinstall Chromium
 browser-use server stop               # Stop any stuck server
 browser-use --headed open <url>       # Try with visible window
 ```
PATCH

echo "Gold patch applied."
