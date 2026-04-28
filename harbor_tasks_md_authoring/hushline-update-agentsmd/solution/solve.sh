#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hushline

# Idempotency guard
if grep -qF "- Before opening a PR, always run `make lint` and `make test` and fix any issues" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -117,8 +117,30 @@ This file provides operating guidance for coding agents working in the Hush Line
 - If tests fail with Postgres shared memory or recovery-mode errors, run `docker compose down -v` and rerun tests on a fresh stack.
 - `dev_data` container is expected to exit after seeding.
 
+## Documentation
+
+When behavior changes or features are added/removed, update documentation:
+
+Local workflow:
+
+1. Clone docs repo:
+   - `git clone https://github.com/scidsg/hushline-docs.git` (if missing)
+   - `cd hushline-docs && git pull --ff-only`
+   - Update, add, or remove relevant documentation content.
+2. Build docs:
+   - `cd docs`
+   - `npm run build`
+3. Clone or update website repo:
+   - `cd ..`
+   - `git clone https://github.com/scidsg/hushline-website.git` (if missing)
+   - `cd hushline-website && git pull --ff-only`
+4. Sync built docs into website library:
+   - `rsync -a --delete ../hushline-docs/docs/build/ ../hushline-website/src/library/`
+5. Verify the site renders correctly before opening PRs.
+
 ## PR Guidance
 
+- Before opening a PR, always run `make lint` and `make test` and fix any issues first.
 - Include what changed.
 - Include why it changed.
 - Include validation commands run.
PATCH

echo "Gold patch applied."
