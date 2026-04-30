#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dashboard

# Idempotency guard
if grep -qF "Gardener Dashboard - Management UI for Gardener Kubernetes clusters. Yarn-manage" "AGENTS.md" && grep -qF "Backend API service for the Gardener Dashboard. Express.js with ESM modules, par" "backend/AGENTS.md" && grep -qF "Frontend client for the Gardener Dashboard. Vue 3 SPA with Vuetify, part of yarn" "frontend/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,13 @@
+# AGENTS.md
+
+Gardener Dashboard - Management UI for Gardener Kubernetes clusters. Yarn-managed monorepo with Vue.js frontend, Node.js backend, and shared packages.
+
+## Essential Commands
+
+```bash
+# Install dependencies
+yarn
+
+# Run verification
+make verify
+```
diff --git a/backend/AGENTS.md b/backend/AGENTS.md
@@ -0,0 +1,19 @@
+# AGENTS.md
+
+Backend API service for the Gardener Dashboard. Express.js with ESM modules, part of yarn monorepo workspace.
+
+## Essential Commands
+
+```bash
+# Start development server
+yarn serve
+
+# Lint code
+yarn lint
+
+# Testing
+yarn build-test-target  # Required: Transpile ESM to CommonJS for tests
+yarn test              # Run tests
+# Or
+yarn test-coverage     # Run tests with coverage report
+```
diff --git a/frontend/AGENTS.md b/frontend/AGENTS.md
@@ -0,0 +1,18 @@
+# AGENTS.md
+
+Frontend client for the Gardener Dashboard. Vue 3 SPA with Vuetify, part of yarn monorepo workspace.
+
+## Essential Commands
+
+```bash
+# Start development server (HTTPS on port 8443)
+yarn serve
+
+# Run tests
+yarn test
+yarn test <PATH TO SPEC FILE>  # Run specific test
+
+# Lint code
+yarn lint
+yarn lint --fix  # Auto-fix issues
+```
PATCH

echo "Gold patch applied."
