#!/usr/bin/env bash
set -euo pipefail

cd /workspace/freya

# Idempotency guard
if grep -qF "- When you are just starting to work on something you must not run any check or " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -38,3 +38,5 @@ Documentation is located in `./crates/freya/src/_docs`.
 - Never push to any branch, much less the `main` branch or using `--force`
 - Never hardcode secrets or any other sensitive data
 - Avoid creating temporary branches unless told
+- When you are just starting to work on something you must not run any check or format command right away, leave that for the end and ask the developer for confirmation
+- Most hooks APIs like `use_state` return `Copy` values like `State`, when moving these around there is no need to `.clone()` them as they are `Copy` already.
PATCH

echo "Gold patch applied."
