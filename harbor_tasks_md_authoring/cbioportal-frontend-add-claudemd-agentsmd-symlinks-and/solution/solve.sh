#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cbioportal-frontend

# Idempotency guard
if grep -qF "When an upstream data source (Genome Nexus, OncoKB, cBioPortal backend) changes " ".github/copilot-instructions.md" && grep -qF ".github/copilot-instructions.md" "AGENTS.md" && grep -qF ".github/copilot-instructions.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -81,6 +81,22 @@ This repository contains the frontend code for cBioPortal, a comprehensive cance
 - **Important**: Reference screenshots created on host system differ from dockerized setup (e.g., CircleCI) and cannot be used as references
 - Failed test screenshots are in `screenshots/diff` and `screenshots/error` folders for debugging
 
+#### Updating stale reference screenshots after an upstream data change
+
+When an upstream data source (Genome Nexus, OncoKB, cBioPortal backend) changes and the e2e reference screenshots go stale, CircleCI will fail on screenshot comparison. The fastest way to refresh the references is to **pull the "actual" screenshot from the failing CircleCI job's artifacts** — that image already shows the new correct data, rendered in the same dockerized environment the reference must match.
+
+```bash
+curl -L 'https://output.circle-artifacts.com/output/job/<job-uuid>/artifacts/0/./screenshots/screen/<screenshot-name>.png' \
+  > 'end-to-end-test/remote/screenshots/reference/<screenshot-name>.png'
+git add 'end-to-end-test/remote/screenshots/reference/<screenshot-name>.png'
+```
+
+Get the `<job-uuid>` from the failing CircleCI check on the PR (click through to the job → Artifacts tab → copy a screenshot URL and extract the UUID).
+
+Don't regenerate screenshots locally unless CircleCI can't produce them — per the note above, host-rendered images won't match the dockerized reference.
+
+Only update the screenshots affected by the upstream change. Don't bundle unrelated screenshot updates. One upstream fix, one PR. PR #5514 (CCDS ID fix) is a reference example.
+
 ### Code Quality
 - Pre-commit hooks automatically format code with Prettier
 - CircleCI runs prettier checks on pull requests
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+.github/copilot-instructions.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+.github/copilot-instructions.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
