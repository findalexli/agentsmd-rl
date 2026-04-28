#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ponyc

# Idempotency guard
if grep -qF "Use the `/pony-release-notes` skill if available. Otherwise: create `.release-no" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -13,6 +13,10 @@ All test commands are slow (full rebuild + test run). Run each command at most o
 - `make test-pony-lint` / `make lint-pony-lint`
 - `make test-pony-doc` / `make lint-pony-doc`
 
+## Release Notes
+
+Use the `/pony-release-notes` skill if available. Otherwise: create `.release-notes/<slug>.md` (e.g., `fix-foo.md`). Do NOT edit `next-release.md` directly — CI aggregates the individual files. Format: `## Title` (matching the PR title exactly) followed by a user-facing description. Include code examples for new API; include before/after for breaking changes.
+
 ## Known Couplings
 
 Non-obvious dependencies between areas of the codebase. When changing code in one of these areas, run the listed test suites before opening a PR — failures here won't be caught by tests local to the area you changed.
PATCH

echo "Gold patch applied."
