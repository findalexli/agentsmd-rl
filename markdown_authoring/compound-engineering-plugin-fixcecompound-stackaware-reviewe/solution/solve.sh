#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- Any code-heavy issue \u2192 always run `compound-engineering:review:code-simplicity" "plugins/compound-engineering/skills/ce-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-compound/SKILL.md b/plugins/compound-engineering/skills/ce-compound/SKILL.md
@@ -260,11 +260,14 @@ After the learning is written and the refresh decision is made, check whether th
 
 Based on problem type, optionally invoke specialized agents to review the documentation:
 
-- **performance_issue** → `performance-oracle`
-- **security_issue** → `security-sentinel`
-- **database_issue** → `data-integrity-guardian`
-- **test_failure** → `cora-test-reviewer`
-- Any code-heavy issue → `kieran-rails-reviewer` + `code-simplicity-reviewer`
+- **performance_issue** → `compound-engineering:review:performance-oracle`
+- **security_issue** → `compound-engineering:review:security-sentinel`
+- **database_issue** → `compound-engineering:review:data-integrity-guardian`
+- Any code-heavy issue → always run `compound-engineering:review:code-simplicity-reviewer`, and additionally run the kieran reviewer that matches the repo's primary stack:
+  - Ruby/Rails → also run `compound-engineering:review:kieran-rails-reviewer`
+  - Python → also run `compound-engineering:review:kieran-python-reviewer`
+  - TypeScript/JavaScript → also run `compound-engineering:review:kieran-typescript-reviewer`
+  - Other stacks → no kieran reviewer needed
 
 </parallel_tasks>
 
@@ -374,9 +377,8 @@ Subagent Results:
 
 Specialized Agent Reviews (Auto-Triggered):
   ✓ performance-oracle: Validated query optimization approach
-  ✓ kieran-rails-reviewer: Code examples meet Rails standards
+  ✓ kieran-rails-reviewer: Code examples meet Rails conventions
   ✓ code-simplicity-reviewer: Solution is appropriately minimal
-  ✓ every-style-editor: Documentation style verified
 
 File created:
 - docs/solutions/performance-issues/n-plus-one-brief-generation.md
@@ -441,20 +443,20 @@ Writes the final learning directly into `docs/solutions/`.
 Based on problem type, these agents can enhance documentation:
 
 ### Code Quality & Review
-- **kieran-rails-reviewer**: Reviews code examples for Rails best practices
-- **code-simplicity-reviewer**: Ensures solution code is minimal and clear
-- **pattern-recognition-specialist**: Identifies anti-patterns or repeating issues
+- **compound-engineering:review:kieran-rails-reviewer**: Reviews code examples for Rails best practices
+- **compound-engineering:review:kieran-python-reviewer**: Reviews code examples for Python best practices
+- **compound-engineering:review:kieran-typescript-reviewer**: Reviews code examples for TypeScript best practices
+- **compound-engineering:review:code-simplicity-reviewer**: Ensures solution code is minimal and clear
+- **compound-engineering:review:pattern-recognition-specialist**: Identifies anti-patterns or repeating issues
 
 ### Specific Domain Experts
-- **performance-oracle**: Analyzes performance_issue category solutions
-- **security-sentinel**: Reviews security_issue solutions for vulnerabilities
-- **cora-test-reviewer**: Creates test cases for prevention strategies
-- **data-integrity-guardian**: Reviews database_issue migrations and queries
-
-### Enhancement & Documentation
-- **best-practices-researcher**: Enriches solution with industry best practices
-- **every-style-editor**: Reviews documentation style and clarity
-- **framework-docs-researcher**: Links to Rails/gem documentation references
+- **compound-engineering:review:performance-oracle**: Analyzes performance_issue category solutions
+- **compound-engineering:review:security-sentinel**: Reviews security_issue solutions for vulnerabilities
+- **compound-engineering:review:data-integrity-guardian**: Reviews database_issue migrations and queries
+
+### Enhancement & Research
+- **compound-engineering:research:best-practices-researcher**: Enriches solution with industry best practices
+- **compound-engineering:research:framework-docs-researcher**: Links to framework/library documentation references
 
 ### When to Invoke
 - **Auto-triggered** (optional): Agents can run post-documentation for enhancement
PATCH

echo "Gold patch applied."
