#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "Do NOT run `/review`, `/qa`, or `/security` automatically. Wait for the user to " "plan/SKILL.md" && grep -qF "After QA is complete and the artifact is saved, tell the user what's next:" "qa/SKILL.md" && grep -qF "After the review is complete and the artifact is saved, tell the user what's nex" "review/SKILL.md" && grep -qF "After the security audit is complete and the artifact is saved, tell the user wh" "security/SKILL.md" && grep -qF "> Ready for `/nano-plan`. Say `/nano-plan` to create the implementation plan, or" "think/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plan/SKILL.md b/plan/SKILL.md
@@ -88,6 +88,19 @@ The `planned_files` list is critical. `/review` uses it for scope drift detectio
 
 The user can disable auto-saving by setting `auto_save: false` in `~/.nanostack/config.json`.
 
+## Next Step
+
+After the user approves the plan and you finish building, tell the user:
+
+> Build complete. Next steps in the sprint:
+> - `/review` to run a two-pass code review with scope drift detection
+> - `/security` to audit for vulnerabilities
+> - `/qa` to test that everything works
+>
+> These three can run in any order. After all pass, `/ship` to create the PR.
+
+Do NOT run `/review`, `/qa`, or `/security` automatically. Wait for the user to invoke each one.
+
 ## Gotchas
 
 - **Don't plan in a vacuum.** The #1 failure mode is planning without reading the code first.
diff --git a/qa/SKILL.md b/qa/SKILL.md
@@ -130,6 +130,15 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 | Regression tests | Skip | If fixing a bug | Full regression suite |
 | WTF threshold | 20% | 20% | 20% |
 
+## Next Step
+
+After QA is complete and the artifact is saved, tell the user what's next:
+
+> QA complete. Remaining steps:
+> - `/review` to run code review (if not done yet)
+> - `/security` to audit for vulnerabilities (if not done yet)
+> - `/ship` to create the PR (after review, security and qa pass)
+
 ## Gotchas
 
 - **Don't test in production.** Always verify you're hitting a local/staging environment.
diff --git a/review/SKILL.md b/review/SKILL.md
@@ -122,6 +122,15 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 | Conflict detection | Auto-resolve | Document inline | BLOCKING until resolved |
 | Output | Blocking issues only | All categories | All + rationale per finding |
 
+## Next Step
+
+After the review is complete and the artifact is saved, tell the user what's next in the sprint:
+
+> Review complete. Remaining steps:
+> - `/security` to audit for vulnerabilities (if not done yet)
+> - `/qa` to test that everything works (if not done yet)
+> - `/ship` to create the PR (after review, security and qa pass)
+
 ## Gotchas
 
 - **If you find zero issues, say so.** Don't manufacture findings to look thorough. "This looks correct and well-structured" is a valid review.
diff --git a/security/SKILL.md b/security/SKILL.md
@@ -226,6 +226,15 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 | Tentative findings | Skip | Skip | Report as TENTATIVE |
 | Confidence gate | 9/10 | 7/10 | 3/10 |
 
+## Next Step
+
+After the security audit is complete and the artifact is saved, tell the user what's next:
+
+> Security audit complete. Remaining steps:
+> - `/review` to run code review (if not done yet)
+> - `/qa` to test that everything works (if not done yet)
+> - `/ship` to create the PR (after review, security and qa pass)
+
 ## Gotchas
 
 - **If you find zero vulnerabilities, say so.** A clean audit is a valid result. Don't manufacture findings to justify the scan.
diff --git a/think/SKILL.md b/think/SKILL.md
@@ -150,6 +150,14 @@ bin/save-artifact.sh think '<json with phase, summary including value_propositio
 
 See `reference/artifact-schema.md` for the full schema. The user can disable auto-saving by setting `auto_save: false` in `~/.nanostack/config.json`.
 
+## Next Step
+
+After the Think Summary and artifact are saved, tell the user:
+
+> Ready for `/nano-plan`. Say `/nano-plan` to create the implementation plan, or adjust the brief first.
+
+Do NOT proceed to planning automatically. Wait for the user to invoke `/nano-plan`.
+
 ## Gotchas
 
 - **Don't skip the diagnostic to "save time."** The diagnostic IS the time savings — it prevents building the wrong thing.
PATCH

echo "Gold patch applied."
