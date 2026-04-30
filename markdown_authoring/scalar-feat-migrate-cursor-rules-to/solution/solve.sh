#!/usr/bin/env bash
set -euo pipefail

cd /workspace/scalar

# Idempotency guard
if grep -qF "description: Minimal starter runbook for cloud agents to install dependencies, r" ".agents/skills/cloud-agents-starter/SKILL.md" && grep -qF "description: Use consistent OpenAPI terminology and definitions when writing doc" ".agents/skills/openapi-glossary/SKILL.md" && grep -qF "description: Write clear, maintainable Vitest and Playwright tests with precise " ".agents/skills/tests/SKILL.md" && grep -qF "description: Write clear, predictable TypeScript and Vue TypeScript code with st" ".agents/skills/typescript/SKILL.md" && grep -qF "description: Build Vue 3 components with TypeScript and Tailwind using clean str" ".agents/skills/vue-components/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/cloud-agents-starter/SKILL.md b/.agents/skills/cloud-agents-starter/SKILL.md
@@ -1,8 +1,8 @@
 ---
-description: Minimal starter skill for Cloud agents - run, test, and navigate the Scalar codebase
-globs: 
-alwaysApply: true
+name: cloud-agents-starter
+description: Minimal starter runbook for cloud agents to install dependencies, run packages, execute tests, and troubleshoot the Scalar monorepo quickly.
 ---
+
 # Cloud Agents Starter Skill - Scalar Codebase
 
 Practical setup and execution instructions for running and testing this codebase. Use this as the first reference when starting the app, running tests, or debugging workflows.
@@ -201,4 +201,4 @@ When you discover new testing tricks, runbook steps, or environment requirements
 4. **Keep it minimal** – only include what agents need to run and test quickly.
 5. **Cross-reference** – if a step depends on another (e.g. test-servers before package tests), state it clearly.
 
-Preferred location for this skill: `.cursor/rules/cloud-agents-starter-skill.mdc`.
+Preferred location for this skill: `.agents/skills/cloud-agents-starter/SKILL.md`.
diff --git a/.agents/skills/openapi-glossary/SKILL.md b/.agents/skills/openapi-glossary/SKILL.md
@@ -1,8 +1,8 @@
 ---
-description: 
-globs: 
-alwaysApply: true
+name: openapi-glossary
+description: Use consistent OpenAPI terminology and definitions when writing documentation, educational material, and tooling guidance.
 ---
+
 # OpenAPI Glossary
 
 > Source: https://github.com/apisyouwonthate/api-glossary
@@ -205,4 +205,4 @@ Historically, "Swagger" was the original name of OpenAPI Specification (OAS). It
 
 Once the Swagger specification was given to [Open API Initiative](mdc:#the-openapi-initiative) in 2016, the name was changed to OpenAPI.
 
-Now, the word "Swagger" is just part of the SwaggerHub brand of tooling. The specification is "OpenAPI" (not OpenAPI/Swagger).
\ No newline at end of file
+Now, the word "Swagger" is just part of the SwaggerHub brand of tooling. The specification is "OpenAPI" (not OpenAPI/Swagger).
diff --git a/.agents/skills/tests/SKILL.md b/.agents/skills/tests/SKILL.md
@@ -1,8 +1,8 @@
 ---
-description: Write awesome tests
-globs: *.test.ts,*.spec.ts,*.e2e-spec.ts,*.e2e.ts
-alwaysApply: false
+name: tests
+description: Write clear, maintainable Vitest and Playwright tests with precise assertions, consistent structure, and strong behavioral coverage.
 ---
+
 # Writing Tests
 
 You write tests that are clear, maintainable, and thorough. You optimize for readability and reliability. Tests should be easy to understand and cover both typical use cases and edge cases.
diff --git a/.agents/skills/typescript/SKILL.md b/.agents/skills/typescript/SKILL.md
@@ -1,8 +1,8 @@
 ---
-description: Write TypeScript code
-globs: *.ts,*.tsx,*.vue
-alwaysApply: false
+name: typescript
+description: Write clear, predictable TypeScript and Vue TypeScript code with strong typing, maintainability, and consistent documentation conventions.
 ---
+
 # Writing TypeScript
 
 You write TypeScript code that is clear, predictable, and easy to maintain. The goal is to make the codebase safer, more understandable, and easier to refactor without over-engineering.
diff --git a/.agents/skills/vue-components/SKILL.md b/.agents/skills/vue-components/SKILL.md
@@ -1,8 +1,8 @@
 ---
-description: Write Vue components
-globs: *.vue
-alwaysApply: false
+name: vue-components
+description: Build Vue 3 components with TypeScript and Tailwind using clean structure, composable logic, accessibility, and maintainable patterns.
 ---
+
 # Writing Vue Components
 
 You are an experienced Vue and TypeScript developer. You write components that are clean, readable, and easy to maintain. You optimize for clarity and simplicity.
PATCH

echo "Gold patch applied."
