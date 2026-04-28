#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xarray

# Idempotency guard
if grep -qF "- **NEVER impersonate the user on GitHub** - Do not post comments, create issues" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -19,3 +19,10 @@ uv run pytest xarray/tests/test_dataarray.py  # Specific file
 pre-commit run --all-files  # Includes ruff and other checks
 uv run dmypy run  # Type checking with mypy
 ```
+
+## GitHub Interaction Guidelines
+
+- **NEVER impersonate the user on GitHub** - Do not post comments, create issues, or interact with the xarray GitHub repository unless explicitly instructed
+- Never create GitHub issues or PRs unless explicitly requested by the user
+- Never post "update" messages, progress reports, or explanatory comments on GitHub issues/PRs unless specifically asked
+- Always require explicit user direction before creating pull requests or pushing to the xarray GitHub repository
PATCH

echo "Gold patch applied."
