#!/usr/bin/env bash
set -euo pipefail

cd /workspace/zen-desktop

# Idempotency guard
if grep -qF "This is the source for Zen - a system-wide proxy-based ad-blocker and privacy gu" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,33 @@
+# AGENTS.md
+
+## About
+
+This is the source for Zen - a system-wide proxy-based ad-blocker and privacy guard. Built using Wails as the application framework, Go for core logic, and TS/React for the UI.
+
+## Commands
+
+Use `task` commands when available.
+
+- Build: `task build-dev`
+- Tests (Go only): `task test`
+- Lint (Go and frontend): `task lint`
+- Lint (frontend only): `task frontend:lint`
+- Format (Go): `task fmt-go`
+- Format check (frontend): `task frontend:fmt`
+
+## File structure
+
+- `main.go` - main application entrypoint
+- `internal/` - core Go application logic
+- `frontend/` - UI
+
+## Working conventions
+
+- Prefer `task` commands over manual shell commands
+- Run `task lint` after changes
+- Run `task test` after Go changes
+
+## Issue and PR guidelines
+
+- Never create an issue
+- Never create a PR
PATCH

echo "Gold patch applied."
