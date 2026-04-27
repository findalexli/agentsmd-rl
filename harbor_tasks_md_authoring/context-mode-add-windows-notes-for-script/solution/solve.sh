#!/usr/bin/env bash
set -euo pipefail

cd /workspace/context-mode

# Idempotency guard
if grep -qF "cmdlets (`Format-List`, `Format-Table`, `Get-Culture`, etc.) do not exist in bas" "configs/codex/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/configs/codex/AGENTS.md b/configs/codex/AGENTS.md
@@ -56,3 +56,22 @@ Search results can flood context. Use `ctx_execute(language: "shell", code: "gre
 | `ctx stats` | Call the `stats` MCP tool and display the full output verbatim |
 | `ctx doctor` | Call the `doctor` MCP tool, run the returned shell command, display as checklist |
 | `ctx upgrade` | Call the `upgrade` MCP tool, run the returned shell command, display as checklist |
+
+## Windows notes
+ 
+**PowerShell cmdlets in shell scripts** — The sandbox executes scripts via bash. PowerShell
+cmdlets (`Format-List`, `Format-Table`, `Get-Culture`, etc.) do not exist in bash and will fail
+with `command not found`. Wrap them with `pwsh -NoProfile -Command "..."` instead.
+ 
+**Relative paths** — The sandbox CWD is a temp directory, not your project root. Always convert
+any user-supplied path to an absolute path before passing it to `rg`, `grep`, or `find`.
+Ask the user to confirm the absolute path if it is not already known.
+ 
+**Windows drive letter paths** — The sandbox runs Git Bash / MSYS2, not WSL. Drive letters must
+use the MSYS2 convention, NOT the WSL convention:
+`X:\path` → `/x/path` (lowercase letter, no `/mnt/` prefix).
+Never emit `/mnt/<letter>/` prefixes regardless of which drive the project is on.
+ 
+**Always quote paths** — If a path contains spaces, bash splits it into separate arguments.
+Always wrap every path in double quotes: `rg "symbol" "$REPO_ROOT/some dir/Source"`.
+This applies to all tools: `rg`, `grep`, `find`, `ls`, etc.
PATCH

echo "Gold patch applied."
