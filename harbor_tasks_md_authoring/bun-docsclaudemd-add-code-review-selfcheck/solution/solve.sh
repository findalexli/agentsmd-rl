#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency guard
if grep -qF "- Before writing code that makes a non-obvious choice, pre-emptively ask \"why th" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -237,6 +237,12 @@ Built-in JavaScript modules use special syntax and are organized as:
 - `internal/` - Internal modules not exposed to users
 - `builtins/` - Core JavaScript builtins (streams, console, etc.)
 
+## Code Review Self-Check
+
+- Before writing code that makes a non-obvious choice, pre-emptively ask "why this and not the alternative?" If you can't answer, research until you can — don't write first and justify later.
+- Don't take a bug report's suggested fix at face value; verify it's the right layer.
+- If neighboring code does something differently than you're about to, find out _why_ before deviating — its choices are often load-bearing, not stylistic.
+
 ## Important Development Notes
 
 1. **Never use `bun test` or `bun <file>` directly** - always use `bun bd test` or `bun bd <command>`. `bun bd` compiles & runs the debug build.
PATCH

echo "Gold patch applied."
