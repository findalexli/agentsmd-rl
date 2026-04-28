#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rdf4j

# Idempotency guard
if grep -qF "* Exception: if no GitHub issue number is available for the task, clearly note t" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -718,6 +718,12 @@ rdf4j: root project
 * Don’t commit or push unless explicitly asked.
 * Don’t add new dependencies without explicit approval.
 
+### Version Control Conventions
+
+* Branch names must always start with the GitHub issue identifier in the form `GH-XXXX`, where `XXXX` is the numeric issue number.
+* Every commit message must be prefixed with the corresponding `GH-XXXX` label.
+* Exception: if no GitHub issue number is available for the task, clearly note this in your handoff and align with the requester on an appropriate branch/commit prefix before proceeding.
+
 It is illegal to `-am` when running tests!
 It is illegal to `-q` when running tests!
 You must follow these rules and instructions exactly as stated.
PATCH

echo "Gold patch applied."
