#!/usr/bin/env bash
set -euo pipefail

cd /workspace/langchain

# Idempotency guard
if grep -qF "Releases are triggered manually via `.github/workflows/_release.yml` with `worki" "AGENTS.md" && grep -qF "Releases are triggered manually via `.github/workflows/_release.yml` with `worki" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -217,6 +217,36 @@ Example partners with profiles in this repo:
 
 The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.
 
+## CI/CD infrastructure
+
+### Release process
+
+Releases are triggered manually via `.github/workflows/_release.yml` with `working-directory` and `release-version` inputs.
+
+### PR labeling and linting
+
+**Title linting** (`.github/workflows/pr_lint.yml`)
+
+**Auto-labeling:**
+
+- `.github/workflows/pr_labeler_file.yml`
+- `.github/workflows/pr_labeler_title.yml`
+- `.github/workflows/auto-label-by-package.yml`
+- `.github/workflows/tag-external-contributions.yml`
+
+### Adding a new partner to CI
+
+When adding a new partner package, update these files:
+
+- `.github/ISSUE_TEMPLATE/*.yml` – Add to package dropdown
+- `.github/dependabot.yml` – Add dependency update entry
+- `.github/pr-file-labeler.yml` – Add file-to-label mapping
+- `.github/workflows/_release.yml` – Add API key secrets if needed
+- `.github/workflows/auto-label-by-package.yml` – Add package label
+- `.github/workflows/check_diffs.yml` – Add to change detection
+- `.github/workflows/integration_tests.yml` – Add integration test config
+- `.github/workflows/pr_lint.yml` – Add to allowed scopes
+
 ## Additional resources
 
 - **Documentation:** https://docs.langchain.com/oss/python/langchain/overview and source at https://github.com/langchain-ai/docs or `../docs/`. Prefer the local install and use file search tools for best results. If needed, use the docs MCP server as defined in `.mcp.json` for programmatic access.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -217,6 +217,36 @@ Example partners with profiles in this repo:
 
 The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.
 
+## CI/CD infrastructure
+
+### Release process
+
+Releases are triggered manually via `.github/workflows/_release.yml` with `working-directory` and `release-version` inputs.
+
+### PR labeling and linting
+
+**Title linting** (`.github/workflows/pr_lint.yml`)
+
+**Auto-labeling:**
+
+- `.github/workflows/pr_labeler_file.yml`
+- `.github/workflows/pr_labeler_title.yml`
+- `.github/workflows/auto-label-by-package.yml`
+- `.github/workflows/tag-external-contributions.yml`
+
+### Adding a new partner to CI
+
+When adding a new partner package, update these files:
+
+- `.github/ISSUE_TEMPLATE/*.yml` – Add to package dropdown
+- `.github/dependabot.yml` – Add dependency update entry
+- `.github/pr-file-labeler.yml` – Add file-to-label mapping
+- `.github/workflows/_release.yml` – Add API key secrets if needed
+- `.github/workflows/auto-label-by-package.yml` – Add package label
+- `.github/workflows/check_diffs.yml` – Add to change detection
+- `.github/workflows/integration_tests.yml` – Add integration test config
+- `.github/workflows/pr_lint.yml` – Add to allowed scopes
+
 ## Additional resources
 
 - **Documentation:** https://docs.langchain.com/oss/python/langchain/overview and source at https://github.com/langchain-ai/docs or `../docs/`. Prefer the local install and use file search tools for best results. If needed, use the docs MCP server as defined in `.mcp.json` for programmatic access.
PATCH

echo "Gold patch applied."
