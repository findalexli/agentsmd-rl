#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "description: Fullstack development toolkit with project scaffolding for Next.js," "engineering-team/senior-fullstack/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/engineering-team/senior-fullstack/SKILL.md b/engineering-team/senior-fullstack/SKILL.md
@@ -1,12 +1,6 @@
 ---
 name: senior-fullstack
-description: >
-  Generates fullstack project boilerplate for Next.js, FastAPI, MERN, and Django
-  stacks, runs static code quality analysis with security and complexity scoring,
-  and guides stack selection decisions. Use when the user asks to "scaffold a
-  project", "create a new app", "set up a starter template", "analyze code
-  quality", "audit my codebase", "what stack should I use", or mentions
-  fullstack boilerplate, project setup, code review, or tech stack comparison.
+description: Fullstack development toolkit with project scaffolding for Next.js, FastAPI, MERN, and Django stacks, code quality analysis with security and complexity scoring, and stack selection guidance. Use when the user asks to "scaffold a new project", "create a Next.js app", "set up FastAPI with React", "analyze code quality", "audit my codebase", "what stack should I use", "generate project boilerplate", or mentions fullstack development, project setup, or tech stack comparison.
 ---
 
 # Senior Fullstack
PATCH

echo "Gold patch applied."
