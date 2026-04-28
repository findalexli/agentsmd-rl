#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencontracts

# Idempotency guard
if grep -qF "5. Don't touch old tests without permission - if pre-existing tests fail after c" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -6,6 +6,11 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 OpenContracts is an AGPL-3.0 enterprise document analytics platform for PDFs and text-based formats. It features a Django/GraphQL backend with PostgreSQL + pgvector, a React/TypeScript frontend with Jotai state management, and pluggable document processing pipelines powered by machine learning models.
 
+## Baseline Commit Rules
+1. Always ensure all affected (or new) tests pass - backend tests suite should only be run in its entirety for good reason as it takes 30+ minutes.
+2. Always make sure typescript compiles and pre-commits pass before committing new code.
+3. Never credit Claude or Claude Code in commit messages, PR messages, etc.
+
 ## Essential Commands
 
 ### Backend (Django)
@@ -212,6 +217,13 @@ docker compose -f production.yml up
    - GraphQL's GenericScalar handles JSON serialization safely
    - Document this requirement in resolver comments
 
+## Critical Concepts
+1. No dead code - when deprecating or replacing code, always try to fully replace older code and, once it's no longer in use, delete it and related texts.
+2. DRY - please always architect code for maximal dryness and always see if you can consolidate related code and remove duplicative code.
+3. Single Responsibility Principle - Generally, ensure that each module / script has a single purpose or related purpose.
+4. No magic numbers - we have constants files in opencontractserver/constants/. Use them for any hardcoded values.
+5. Don't touch old tests without permission - if pre-existing tests fail after changes, try to identify why and present user with root cause analysis. If the test logic is correct but expectations need updating due to intentional behavior changes, document the change clearly.
+
 ## Testing Patterns
 
 ### Backend Tests
@@ -265,9 +277,11 @@ const component = await mount(
 
 ## Branch Strategy
 
-- **Development**: PRs target `v3.0.0.b3` branch (NOT main)
-- **Production**: `main` branch
-- Use feature branches: `feature/description-issue-number`
+This project follows **trunk-based development**:
+
+- Work directly on `main` branch or use short-lived feature branches
+- Feature branches: `feature/description-issue-number`
+- Merge feature branches quickly (within a day or two)
 - Commit message format: Descriptive with issue references (e.g., "Closes #562")
 
 ## Changelog Maintenance
PATCH

echo "Gold patch applied."
