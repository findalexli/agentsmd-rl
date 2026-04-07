#!/usr/bin/env bash
set -euo pipefail

cd /workspace/infisical

# Idempotent: skip if already applied
if grep -q 'Dependency Policy' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -43,6 +43,10 @@ Infisical supports self-hosted deployment via Docker. Key considerations:
 - **`docker-compose.prod.yml`** — production compose with backend, PostgreSQL, and Redis.
 - New backend dependencies should be evaluated carefully — they affect container size, FIPS compliance, and the encryption boundary. Check `docs/` for self-hosted deployment documentation when in doubt.

+### Dependency Policy
+
+Both `backend/` and `frontend/` enforce a minimum release age of 7 days for npm packages (configured via `.npmrc` in each directory). This means `npm install` will only resolve package versions published at least 7 days ago, as a supply-chain security measure.
+
 ## Cross-Cutting Patterns

 ### Auth & Permissions
diff --git a/backend/.npmrc b/backend/.npmrc
new file mode 100644
--- /dev/null
+++ b/backend/.npmrc
@@ -0,0 +1 @@
+min-release-age=7
diff --git a/frontend/.npmrc b/frontend/.npmrc
new file mode 100644
--- /dev/null
+++ b/frontend/.npmrc
@@ -0,0 +1 @@
+min-release-age=7
diff --git a/backend/package.json b/backend/package.json
--- a/backend/package.json
+++ b/backend/package.json
@@ -5,6 +5,9 @@
   "description": "",
   "main": "./dist/main.mjs",
+  "engines": {
+    "npm": ">=11.10.0"
+  },
   "scripts": {
     "assets:export": "./scripts/export-assets.sh",
     "test": "echo \"Error: no test specified\" && exit 1",
diff --git a/frontend/package.json b/frontend/package.json
--- a/frontend/package.json
+++ b/frontend/package.json
@@ -4,6 +4,9 @@
   "private": true,
   "version": "0.0.0",
   "type": "module",
+  "engines": {
+    "npm": ">=11.10.0"
+  },
   "scripts": {
     "dev": "vite",
     "build": "tsc -b && vite build",

PATCH

echo "Patch applied successfully."
