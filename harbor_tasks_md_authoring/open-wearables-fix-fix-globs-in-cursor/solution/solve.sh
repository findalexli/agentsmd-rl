#!/usr/bin/env bash
set -euo pipefail

cd /workspace/open-wearables

# Idempotency guard
if grep -qF "globs: backend/app/models/**,backend/app/database.py,backend/app/mappings.py,bac" "backend/.cursor/rules/models.mdc" && grep -qF "globs: backend/app/repositories/**" "backend/.cursor/rules/repositories.mdc" && grep -qF "globs: backend/app/api/routes/**" "backend/.cursor/rules/routes.mdc" && grep -qF "globs: backend/app/schemas/**" "backend/.cursor/rules/schemas.mdc" && grep -qF "globs: backend/app/services/**,backend/app/utils/exceptions.py" "backend/.cursor/rules/services.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/backend/.cursor/rules/models.mdc b/backend/.cursor/rules/models.mdc
@@ -1,5 +1,5 @@
 ---
-globs: app/models/**,app/database.py,app/mappings.py,app/utils/mappings_meta.py
+globs: backend/app/models/**,backend/app/database.py,backend/app/mappings.py,backend/app/utils/mappings_meta.py
 alwaysApply: false
 ---
 
diff --git a/backend/.cursor/rules/repositories.mdc b/backend/.cursor/rules/repositories.mdc
@@ -1,5 +1,5 @@
 ---
-globs: app/repositories/**
+globs: backend/app/repositories/**
 alwaysApply: false
 ---
 
diff --git a/backend/.cursor/rules/routes.mdc b/backend/.cursor/rules/routes.mdc
@@ -1,5 +1,5 @@
 ---
-globs: app/api/routes/**
+globs: backend/app/api/routes/**
 alwaysApply: false
 ---
 
diff --git a/backend/.cursor/rules/schemas.mdc b/backend/.cursor/rules/schemas.mdc
@@ -1,5 +1,5 @@
 ---
-globs: app/schemas/**
+globs: backend/app/schemas/**
 alwaysApply: false
 ---
 
diff --git a/backend/.cursor/rules/services.mdc b/backend/.cursor/rules/services.mdc
@@ -1,5 +1,5 @@
 ---
-globs: app/services/**,app/utils/exceptions.py
+globs: backend/app/services/**,backend/app/utils/exceptions.py
 alwaysApply: false
 ---
 
PATCH

echo "Gold patch applied."
