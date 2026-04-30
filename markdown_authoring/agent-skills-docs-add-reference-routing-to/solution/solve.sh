#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "- For detailed security review guidance, see `references/security-checklist.md`" "skills/code-review-and-quality/SKILL.md" && grep -qF "For detailed accessibility requirements and testing tools, see `references/acces" "skills/frontend-ui-engineering/SKILL.md" && grep -qF "For detailed performance checklists, optimization commands, and anti-pattern ref" "skills/performance-optimization/SKILL.md" && grep -qF "For detailed security checklists and pre-commit verification steps, see `referen" "skills/security-and-hardening/SKILL.md" && grep -qF "- For accessibility verification before launch, see `references/accessibility-ch" "skills/shipping-and-launch/SKILL.md" && grep -qF "For detailed testing patterns, examples, and anti-patterns across frameworks, se" "skills/test-driven-development/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/code-review-and-quality/SKILL.md b/skills/code-review-and-quality/SKILL.md
@@ -310,6 +310,10 @@ Part of code review is dependency review:
 - [ ] **Approve** — Ready to merge
 - [ ] **Request changes** — Issues must be addressed
 ```
+## See Also
+
+- For detailed security review guidance, see `references/security-checklist.md`
+- For performance review checks, see `references/performance-checklist.md`
 
 ## Common Rationalizations
 
diff --git a/skills/frontend-ui-engineering/SKILL.md b/skills/frontend-ui-engineering/SKILL.md
@@ -286,6 +286,10 @@ function useToggleTask() {
 }
 ```
 
+## See Also
+
+For detailed accessibility requirements and testing tools, see `references/accessibility-checklist.md`.
+
 ## Common Rationalizations
 
 | Rationalization | Reality |
diff --git a/skills/performance-optimization/SKILL.md b/skills/performance-optimization/SKILL.md
@@ -248,6 +248,11 @@ npx bundlesize --config bundlesize.config.json
 npx lhci autorun
 ```
 
+## See Also
+
+For detailed performance checklists, optimization commands, and anti-pattern reference, see `references/performance-checklist.md`.
+
+
 ## Common Rationalizations
 
 | Rationalization | Reality |
diff --git a/skills/security-and-hardening/SKILL.md b/skills/security-and-hardening/SKILL.md
@@ -312,6 +312,9 @@ git diff --cached | grep -i "password\|secret\|api_key\|token"
 - [ ] Dependencies audited for vulnerabilities
 - [ ] Error messages don't expose internals
 ```
+## See Also
+
+For detailed security checklists and pre-commit verification steps, see `references/security-checklist.md`.
 
 ## Common Rationalizations
 
diff --git a/skills/shipping-and-launch/SKILL.md b/skills/shipping-and-launch/SKILL.md
@@ -263,6 +263,11 @@ Every deployment needs a rollback plan before it happens:
 - Redeploy previous version: < 5 minutes
 - Database rollback: < 15 minutes
 ```
+## See Also
+
+- For security pre-launch checks, see `references/security-checklist.md`
+- For performance pre-launch checklist, see `references/performance-checklist.md`
+- For accessibility verification before launch, see `references/accessibility-checklist.md`
 
 ## Common Rationalizations
 
diff --git a/skills/test-driven-development/SKILL.md b/skills/test-driven-development/SKILL.md
@@ -342,6 +342,10 @@ then verifies the test passes.
 
 This separation ensures the test is written without knowledge of the fix, making it more robust.
 
+## See Also
+
+For detailed testing patterns, examples, and anti-patterns across frameworks, see `references/testing-patterns.md`.
+
 ## Common Rationalizations
 
 | Rationalization | Reality |
PATCH

echo "Gold patch applied."
