#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-governance-toolkit

# Idempotency guard
if grep -qF "- To look up a Docker image digest: `docker pull python:3.12-slim && docker insp" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -60,6 +60,65 @@ Before approving or merging ANY PR, verify ALL of the following:
 
 ## Security Rules
 
+### Code Scanning Prevention (Scorecard + CodeQL)
+
+These rules prevent the exact alert categories that code scanning flags. Every PR
+and commit MUST comply — CI will catch violations, but catching them before push
+saves time.
+
+**Pinned Dependencies (Scorecard PinnedDependenciesID):**
+- All GitHub Actions MUST be pinned by full SHA hash, never bare tags:
+  - ✅ `uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4`
+  - ❌ `uses: actions/checkout@v4`
+- All Docker FROM images MUST include `@sha256:` digest:
+  - ✅ `FROM python:3.12-slim@sha256:804ddf3251a60bbf9c92e73b7566c40428d54d0e79d3428194edf40da6521286`
+  - ❌ `FROM python:3.12-slim`
+- All `pip install` in workflows, Dockerfiles, and shell scripts MUST pin versions:
+  - ✅ `pip install mkdocs-material==9.7.6`
+  - ❌ `pip install mkdocs-material`
+- To look up a GitHub Action SHA: `gh api repos/{owner}/{repo}/git/ref/tags/{tag} --jq '.object.sha'`
+- To look up a Docker image digest: `docker pull python:3.12-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.12-slim`
+
+**Token Permissions (Scorecard TokenPermissionsID):**
+- All workflow files MUST have explicit `permissions:` at the top level
+- Top-level permissions MUST be `contents: read` only (least privilege)
+- Write permissions (`packages: write`, `pull-requests: write`, `id-token: write`, etc.)
+  MUST be scoped to the specific job that needs them, not the workflow level:
+  ```yaml
+  # ✅ CORRECT — write scoped to job
+  permissions:
+    contents: read
+  jobs:
+    publish:
+      permissions:
+        packages: write
+  
+  # ❌ WRONG — write at top level
+  permissions:
+    contents: read
+    packages: write
+  ```
+
+**Python Code Quality (CodeQL):**
+- Never use `timedelta(days=365)` to represent "one year" — use `timedelta(days=366)`
+  or `dateutil.relativedelta(years=1)` for leap-year safety
+- Never use `is True` / `is False` for boolean comparison — use `== True` / `== False`
+  (or just `if value:` / `if not value:`)
+- Never use mutable default arguments (`def f(x=[])`) — use `None` with body initialization:
+  ```python
+  # ✅ def f(x=None): x = x or []
+  # ❌ def f(x=[]):
+  ```
+- Remove unnecessary `pass` statements in non-empty function/class bodies
+
+**TypeScript/JavaScript Code Quality (CodeQL):**
+- URL validation MUST use `new URL()` constructor or protocol-aware checks, never
+  plain substring matching:
+  - ✅ `new URL(href).hostname === 'cdn.jsdelivr.net'`
+  - ❌ `href.includes('cdn.jsdelivr.net')`
+
+### General Security Rules
+
 - All `pip install` commands must reference registered PyPI packages
 - All security patterns must be in YAML config, not hardcoded
 - All GitHub Actions must be SHA-pinned (use `action@<sha> # vX.Y.Z` format, never bare tags like `@v46`)
PATCH

echo "Gold patch applied."
