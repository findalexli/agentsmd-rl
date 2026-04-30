#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "stacks, runs static code quality analysis with security and complexity scoring," "engineering-team/senior-fullstack/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/engineering-team/senior-fullstack/SKILL.md b/engineering-team/senior-fullstack/SKILL.md
@@ -1,6 +1,12 @@
 ---
 name: senior-fullstack
-description: Fullstack development toolkit with project scaffolding for Next.js/FastAPI/MERN/Django stacks and code quality analysis. Use when scaffolding new projects, analyzing codebase quality, or implementing fullstack architecture patterns.
+description: >
+  Generates fullstack project boilerplate for Next.js, FastAPI, MERN, and Django
+  stacks, runs static code quality analysis with security and complexity scoring,
+  and guides stack selection decisions. Use when the user asks to "scaffold a
+  project", "create a new app", "set up a starter template", "analyze code
+  quality", "audit my codebase", "what stack should I use", or mentions
+  fullstack boilerplate, project setup, code review, or tech stack comparison.
 ---
 
 # Senior Fullstack
@@ -169,35 +175,39 @@ Total Lines: 12,500
 
 ### Workflow 1: Start New Project
 
-1. Choose appropriate stack based on requirements
+1. Choose appropriate stack based on requirements (see Stack Decision Matrix)
 2. Scaffold project structure
-3. Run initial quality check
-4. Set up development environment
+3. Verify scaffold: confirm `package.json` (or `requirements.txt`) exists
+4. Run initial quality check — address any P0 issues before proceeding
+5. Set up development environment
 
 ```bash
 # 1. Scaffold project
 python scripts/project_scaffolder.py nextjs my-saas-app
 
-# 2. Navigate and install
+# 2. Verify scaffold succeeded
+ls my-saas-app/package.json
+
+# 3. Navigate and install
 cd my-saas-app
 npm install
 
-# 3. Configure environment
+# 4. Configure environment
 cp .env.example .env.local
 
-# 4. Run quality check
+# 5. Run quality check
 python ../scripts/code_quality_analyzer.py .
 
-# 5. Start development
+# 6. Start development
 npm run dev
 ```
 
 ### Workflow 2: Audit Existing Codebase
 
 1. Run code quality analysis
-2. Review security findings
-3. Address critical issues first
-4. Plan improvements
+2. Review security findings — fix all P0 (critical) issues immediately
+3. Re-run analyzer to confirm P0 issues are resolved
+4. Create tickets for P1/P2 issues
 
 ```bash
 # 1. Full analysis
@@ -206,8 +216,8 @@ python scripts/code_quality_analyzer.py /path/to/project --verbose
 # 2. Generate detailed report
 python scripts/code_quality_analyzer.py /path/to/project --json --output audit.json
 
-# 3. Address P0 issues immediately
-# 4. Create tickets for P1/P2 issues
+# 3. After fixing P0 issues, re-run to verify
+python scripts/code_quality_analyzer.py /path/to/project --verbose
 ```
 
 ### Workflow 3: Stack Selection
PATCH

echo "Gold patch applied."
