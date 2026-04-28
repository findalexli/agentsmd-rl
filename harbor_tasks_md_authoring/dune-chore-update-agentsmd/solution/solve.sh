#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dune

# Idempotency guard
if grep -qF "- Do not write `to_dyn` functions. Write `Repr.t` values and use those to" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -132,7 +132,8 @@ This output will appear in cram test diffs, making it easy to observe values.
 - Qualify record construction: `{ Module.field = value }`
 - Prefer destructuring over projection: `let { Module.field; _ } = record` not
   `record.Module.field`
-- Pattern match exhaustively in `to_dyn` functions: `let to_dyn {a; b; c} = ...`
+- Do not write `to_dyn` functions. Write `Repr.t` values and use those to
+  construct `to_dyn`.
 
 ## Critical Constraints
 
@@ -143,6 +144,8 @@ This output will appear in cram test diffs, making it easy to observe values.
 - NEVER run `dune clean`
 - NEVER use the `--force` argument
 - NEVER try to build dune manually to run a test
+- NEVER run dune in parallel
+- NEVER delete the dune lock file
 
 **ALWAYS do these things:**
 - ALWAYS prefer editing existing files over creating new ones
PATCH

echo "Gold patch applied."
