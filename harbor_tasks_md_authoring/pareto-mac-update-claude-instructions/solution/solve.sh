#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pareto-mac

# Idempotency guard
if grep -qF "- `debug` - Output detailed check status (supports `?check=<checkname>` paramete" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -69,11 +69,14 @@ This project uses SwiftLint for style enforcement and SwiftFormat for auto-forma
 The app supports custom URL scheme `paretosecurity://` for:
 - `reset` - Reset to default settings
 - `showMenu` - Open status bar menu
-- `update` - Force update check
+- `update` - Force update check (not available in SetApp build)
 - `welcome` - Show welcome window
 - `runChecks` - Trigger security checks
-- `debug` - Output detailed check status
+- `debug` - Output detailed check status (supports `?check=<checkname>` parameter)
 - `logs` - Copy system logs
+- `showPrefs` - Show preferences window
+- `showBeta` - Enable beta channel
+- `enrollTeam` - Enroll device to team (not available in SetApp build)
 
 ## Testing Strategy
 - Unit tests in `ParetoSecurityTests/` cover core functionality
PATCH

echo "Gold patch applied."
