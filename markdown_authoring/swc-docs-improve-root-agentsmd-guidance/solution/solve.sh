#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swc

# Idempotency guard
if grep -qF "-   After addressing pull request review comments and pushing updates, resolve t" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -14,11 +14,30 @@
 -   Write documentation for your code.
 -   Commit your work as frequent as possible using git. Do NOT use `--no-verify` flag.
 -   Prefer multiple small files over single large file.
+-   Prefer enum (or dedicated type) based modeling over raw string literals whenever possible.
 
 ---
 
 -   When creating Atom instances, it's better to use `Cow<str>` or `&str` instead of `String`. Note that `&str` is better than `Cow<str>` here.
 
+## Debugging and logging
+
+-   Do not guess behavior. Verify assumptions by reading source, fixtures, and tests.
+-   Debug with logs when behavior is unclear.
+-   Write sufficient logs for debugging and operational troubleshooting.
+-   Prefer structured logging in Rust (`tracing`) over ad-hoc plain text logs when feasible.
+
+## Shell safety
+
+-   For shell commands or scripts, prefer `$(...)` over legacy backticks for command substitution.
+-   Quote and escape all dynamic shell values strictly.
+
+## Git workflow
+
+-   Run `git commit` only after `git add`.
+-   Once changes are staged, commit without unnecessary delay so staged history is preserved.
+-   After addressing pull request review comments and pushing updates, resolve the corresponding review threads.
+
 ## Testing
 
 -   Write unit tests for your code.
PATCH

echo "Gold patch applied."
