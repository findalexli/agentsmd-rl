#!/usr/bin/env bash
set -euo pipefail

cd /workspace/daft

# Idempotency guard
if grep -qF "- Titles: Conventional Commits (e.g., `feat: ...`); enforced by `.github/workflo" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -24,3 +24,8 @@
     - `make test EXTRA_ARGS="-v tests/dataframe/test_select.py::test_select_dataframe"` runs the given test method.
   -  Default `integration`, `benchmark`, and `hypothesis` tests are disabled. Best to run on CI.
 - `make doctests` runs doctests in `daft/` directory. Tests docstrings in Daft APIs.
+
+## PR Conventions
+
+- Titles: Conventional Commits (e.g., `feat: ...`); enforced by `.github/workflows/pr-labeller.yml`.
+- Descriptions: follow `.github/pull_request_template.md`.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
