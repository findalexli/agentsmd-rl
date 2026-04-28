#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effection

# Idempotency guard
if grep -qF "changes to files that direct the behavior of AI such as AGENTS.md or llms.txt" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -372,6 +372,12 @@ for (const item of yield * each(stream(asyncIterable))) {
 - After resolve/reject, yielding the `operation` always produces the same
   outcome; calling resolve/reject again has no effect.
 
+## Commit and PR conventions
+
+Use [gitmoji](https://gitmoji.dev) for commit and pull request subjects. For
+changes to files that direct the behavior of AI such as AGENTS.md or llms.txt
+use a robot emoji instead of the standard gitmoji for documentation
+
 ## Pre-commit workflow
 
 Before committing any changes to this repository:
PATCH

echo "Gold patch applied."
