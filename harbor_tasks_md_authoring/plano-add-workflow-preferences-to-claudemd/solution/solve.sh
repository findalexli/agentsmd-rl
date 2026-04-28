#!/usr/bin/env bash
set -euo pipefail

cd /workspace/plano

# Idempotency guard
if grep -qF "- **Git commits:** Do NOT add `Co-Authored-By` lines. Keep commit messages short" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -137,6 +137,12 @@ To prepare a release (e.g., bumping from `0.4.6` to `0.4.7`), update the version
 
 Commit message format: `release X.Y.Z`
 
+## Workflow Preferences
+
+- **Git commits:** Do NOT add `Co-Authored-By` lines. Keep commit messages short and concise (one line, no verbose descriptions). NEVER commit and push directly to `main`—always use a feature branch and PR.
+- **Git branches:** Use the format `<github_username>/<feature_name>` when creating branches for PRs. Determine the username from `gh api user --jq .login`.
+- **GitHub issues:** When a GitHub issue URL is pasted, fetch all requirements and context from the issue first. The end goal is always a PR with all tests passing.
+
 ## Key Conventions
 
 - Rust edition 2021, formatted with `cargo fmt`, linted with `cargo clippy -D warnings`
PATCH

echo "Gold patch applied."
